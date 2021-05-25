import csv
import datetime


from django.contrib.auth.decorators import login_required, permission_required
from ..models import Idea, IdeaPhase
from django.shortcuts import render
from django.db.models import Q
from ..forms import ReportForm, HiddenReportForm
from django.http import StreamingHttpResponse
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages

@login_required
@permission_required('ideax.manage_idea', raise_exception=True)
def view_report_ideas(request):
    ideas=[]
    form = ReportForm()
    form2 = HiddenReportForm()

    if request.method == "POST":
        form = ReportForm(request.POST)
        phases = IdeaPhase.objects.all()
        form.fields['phase'].choices = [('', '---------')] + [(phase.id, phase.name) for phase in phases]
        if form.is_valid():
            data_inicial = form.cleaned_data['start_date']
            data_final = form.cleaned_data['end_date']
            autor = form.cleaned_data['author']
            fase = form.cleaned_data['phase']
            apagadas = form.cleaned_data['discarded']
            form2 = HiddenReportForm()
            if data_inicial:
                form2.fields['st'].initial = data_inicial.strftime("%d/%m/%Y")
            if data_final:
                form2.fields['en'].initial = data_final.strftime("%d/%m/%Y")
            form2.fields['au'].initial = autor
            form2.fields['ph'].initial = fase
            form2.fields['ds'].initial = apagadas
            filtro_basico = monta_filtros(autor, data_inicial, data_final, apagadas, fase)
            ideas = Idea.objects.filter(filtro_basico).order_by('id').distinct()
            if not ideas.exists():
                messages.error(request, _('No results were found for your search!'))
    else:
        phases = IdeaPhase.objects.all()
        form.fields['phase'].choices = [('', '---------')] + [(phase.id, phase.name) for phase in phases]
    return render(request, 'ideax/report/report_view.html', {'ideas': ideas, 'form': form, 'filtros': form2})

def monta_filtros(autor, data_inicial, data_final, apagadas, fase):
    filtro_basico = (Q(authors__user__first_name__icontains=autor) | Q(authors__user__last_name__icontains=autor)
                    | Q(authors__user__username__icontains=autor))
    if data_inicial and not data_final:
        data_inicial = datetime.datetime.combine(data_inicial, datetime.time.min)
        filtro_basico.add(Q(creation_date__gte=data_inicial), Q.AND)
    elif data_final and not data_inicial:
        data_final = datetime.datetime.combine(data_final, datetime.time.max)
        filtro_basico.add(Q(creation_date__lte=data_final), Q.AND)
    elif data_inicial and data_final:
        data_inicial = datetime.datetime.combine(data_inicial, datetime.time.min)
        data_final = datetime.datetime.combine(data_final, datetime.time.max)
        filtro_basico.add(Q(creation_date__range=(data_inicial,data_final)), Q.AND)
    if not apagadas:
        filtro_basico.add(Q(discarded=False), Q.AND)
    if fase:
        filtro_basico.add(Q(phase_history__current_phase=fase,phase_history__current=1), Q.AND)
    return filtro_basico


@login_required
@permission_required('ideax.manage_idea', raise_exception=True)
def export_report(request):
    form = HiddenReportForm(request.POST)
    phases = IdeaPhase.objects.all()
    form.fields['ph'].choices = [('', '---------')] + [(phase.id, phase.name) for phase in phases]
    if form.is_valid():
        data_inicial = form.cleaned_data['st']
        data_final = form.cleaned_data['en']
        autor = form.cleaned_data['au']
        fase = form.cleaned_data['ph']
        apagadas = form.cleaned_data['ds']
        filtro_basico = monta_filtros(autor, data_inicial, data_final, apagadas, fase)

        csv_path = 'RELATORIO_IDEIAS.csv'
        with open(csv_path, 'w', newline='', encoding='utf-8') as f_handle:
            writer = csv.writer(f_handle)
            header = [
                'id',
                _('Title'),
                _('Date of registration'),
                _('Author'),
                _('Idea Phase'),
                _('Grade')
            ]
            writer.writerow(header)
            for idea in Idea.objects.filter(filtro_basico).order_by('id').distinct():
                authors = [author.user.username for author in idea.authors.all()]
                phase = idea.phase_history_set.filter(current=True).first()
                row = [idea.id, idea.title, idea.creation_date, ",".join(authors), phase.current_phase.name, idea.score]
                writer.writerow(row)

            response = StreamingHttpResponse(open(csv_path), content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename=' + csv_path
            return response


# <th > Id < /th >
#       <th > { % trans 'Title' % } < /th >
#       <th > { % trans 'Date of registration' % } < /th >
#       <th > { % trans 'Author' % } < /th >
#       <th > { % trans 'Idea Phase' % } < /th >
#       <th > { % trans 'Grade' % } < /th >
