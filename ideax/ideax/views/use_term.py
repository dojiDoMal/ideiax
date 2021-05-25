from django.http import JsonResponse
from datetime import date

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _ # noqa

from ...users.models import UserProfile
from ...util import audit, get_client_ip, get_ip
from ..forms import UseTermForm
from ..models import Use_Term


class UseTermHelper:
    @classmethod
    def get_use_term_list(cls):
        return {'use_term_list': Use_Term.objects.all(), 'today': date.today()}


@login_required
def accept_use_term(request):
    if not request.user.userprofile.use_term_accept:
        user_profile = UserProfile.objects.get(user=request.user)
        user_profile.use_term_accept = True
        user_profile.acceptance_date = timezone.localtime(timezone.now())
        user_profile.ip = get_ip(request)
        user_profile.save()
        messages.success(request, _('Term of use accepted!'))
        # logger.info('%(username)s|%(ip_addr)s|%(message)s', {
        # 'username': request.user.username, 'ip_addr': get_client_ip(request), 'message': 'Term of use accepted!'})
    else:
        messages.success(request, _('Term of use already accepted!'))
        # logger.info('%(username)s|%(ip_addr)s|%(message)s', {
        # 'username': request.user.username, 'ip_addr': get_client_ip(request),
        # 'message': 'Term of use already accepted!'})

    audit(request.user.username, get_client_ip(request), 'ACCEPT_TERMS_OF_USE_OPERATION', UserProfile.__name__, '')
    return redirect('index')


@login_required
@permission_required('ideax.add_use_term', raise_exception=True)
def use_term_new(request):
    if request.method == "POST":
        form = UseTermForm(request.POST)
    else:
        form = UseTermForm()
    return save_use_term(request, form, 'ideax/use_term_new.html', True)


@login_required
@permission_required('ideax.change_use_term', raise_exception=True)
def use_term_edit(request, pk):
    use_term = get_object_or_404(Use_Term, pk=pk)
    if request.method == "POST":
        use_term_form = UseTermForm(request.POST, instance=use_term)
    else:
        use_term_form = UseTermForm(instance=use_term)
    return save_use_term(request, use_term_form, 'ideax/use_term_edit.html')


def save_use_term(request, form, template_name, new=False):
    if request.method == "POST":
        if form.is_valid():
            use_term = form.save(commit=False)
            use_term.creator = UserProfile.objects.get(user=request.user)
            if use_term.is_invalid_date():
                messages.error(request, _('Invalid Final Date'))
                return render(request, template_name, {'form': form})
            if Use_Term.objects.get_active() and new:
                messages.error(request, _('Already exists a active Term Of Use'))
                return render(request, template_name, {'form': form})
            use_term.save()
            set_invalid_use_term(request)
            messages.success(request, _('Term of Use saved successfully!'))
            return redirect('use_term_list')
    else:
        return render(request, template_name, {'form': form})


@login_required
def set_invalid_use_term(request):
    users = UserProfile.objects.filter(user__is_staff=False)
    for user in users:
        user.use_term_accept = False
        user.save()


@login_required
@permission_required('ideax.delete_use_term', raise_exception=True)
def use_term_remove(request, pk):
    use_term = get_object_or_404(Use_Term, pk=pk)
    if request.method == 'GET':
        use_term.final_date = timezone.now()
        use_term.save()
        messages.success(request, _('Terms of Use removed successfully!'))
        return render(request, 'ideax/use_term_list.html', UseTermHelper.get_use_term_list())


@login_required
def use_term_detail(request, pk):
    use_term = get_object_or_404(Use_Term, pk=pk)
    return render(request, 'ideax/use_term_detail.html', {'use_term': use_term})


@login_required
def use_term_list(request):
    return render(request, 'ideax/use_term_list.html', UseTermHelper.get_use_term_list())


def get_valid_use_term(request):
    use_terms = Use_Term.objects.all()
    for term in use_terms:
        if term.is_past_due:
            valid_use_term = term
            return render(request, 'ideax/use_term.html', {'use_term': valid_use_term})
    return render(request, 'ideax/use_term.html', {'use_term': _("No Term of Use found")})


def get_term_of_user(request):
    term = Use_Term.objects.filter(final_date__gte=timezone.now())
    if term.exists():
        return JsonResponse({"term": term[0].term})
    return JsonResponse({"term": _("No Term of Use found")})


def term_of_user_exist():
    return Use_Term.objects.filter(final_date__gte=timezone.now()).exists()
