import os
import json
import uuid
import collections
import mistune
import csv
import urllib


from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.db.models import Count, Case, When, Q
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _ # noqa
from django.http import HttpResponse
from django.conf import settings
from django.core.files.storage import FileSystemStorage, default_storage
from django.db import connection
from django.http import StreamingHttpResponse
from django.core.files.base import ContentFile
from ideax.settings.django._core import GOOGLE_RECAPTCHA_SECRET_KEY, GOOGLE_RECAPTCHA_URL
from martor.utils import LazyEncoder, markdownify
from bs4 import BeautifulSoup
from notifications.signals import notify
from functools import reduce 

from ...users.models import UserProfile, AuthConfiguration
from ...users.views import set_authconfiguration
from ..models import (
    Idea, Criterion, Popular_Vote, Phase_History, IdeaPhase,
    Comment, Evaluation, Category_Image, Challenge, Dimension,
    Follow,
)
from ..forms import IdeaForm, CriterionForm, EvaluationForm, ChallengeForm, IdeaPhaseForm
from ...singleton import ProfanityCheck
from ...mail_util import MailUtil
from ...util import get_ip, get_client_ip, audit
from ..enums import EvaluationPhase, UserEditCommentsProfile, NotificationType
from ..helpers import update_evaluation_phase, CommentsHelper, FollowHelper, is_same_author, RelationShipHelper
from ..idea_notification import message_menager
from ..validators import check_comment

from .category import (
    category_edit,
    category_list,
    category_new,
    category_remove
)
from .category_image import category_image_edit, category_image_list, category_image_new, category_image_remove
from .use_term import (
    get_term_of_user, accept_use_term, get_valid_use_term, save_use_term,
    use_term_detail, use_term_edit, use_term_list, use_term_new, use_term_remove,
    term_of_user_exist
)
from .dimension import dimension_new, dimension_list, dimension_edit, dimension_remove
from .report import view_report_ideas, export_report

mail_util = MailUtil()


def index(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            if AuthConfiguration.objects.filter(active=True) and term_of_user_exist():
                pass
            else:
                return set_authconfiguration(request, True)
        audit(request.user.username, get_client_ip(request), 'LIST_IDEAS_PAGE', Idea.__name__, '')
        return idea_list(request)
    return render(request, 'ideax/index.html')


def mark_notifications_as_read(request):
    notifications = request.user.notifications.unread()
    notifications.mark_all_as_read()
    data = {
            'size': 0
           }
    return JsonResponse(data)


@login_required
def idea_list(request):

    ideas = get_ideas_init(request)
    ideas['idea_phase'] = get_phases_count()
    # page = request.GET.get('page', 1)
    # paginator = Paginator(ideas['ideas'], 5)

    # try:
    #     ideas['ideas'] = paginator.page(page)
    # except PageNotAnInteger:
    #     ideas['ideas'] = paginator.page(1)
    # except EmptyPage:
    #     ideas['ideas'] = paginator.page(paginator.num_pages)
    return render(request, 'ideax/idea_list.html', ideas)


def get_phases_count():
    return IdeaPhase.objects.annotate(qtd=Count("phase_history__idea_id",
                                      filter=Q(phase_history__idea__discarded=False, phase_history__current=1))
                                      ).order_by('order')


@login_required
def get_ideas_init(request):
    ideas_dic = dict()
    ideas_dic['phase_req'] = IdeaPhase.objects.values('id').get(order=1)['id']
    ideas_dic['ideas'] = Idea.objects.filter(
        discarded=False,
        phase_history__current_phase=ideas_dic['phase_req'],
        phase_history__current=1).annotate(
            count_like=Count(Case(When(popular_vote__like=True, then=1)))).order_by('-count_like')
    ideas_dic['ideas_liked'] = get_ideas_voted(request, True)
    ideas_dic['ideas_disliked'] = get_ideas_voted(request, False)
    ideas_dic['ideas_created_by_me'] = get_ideas_created(request)
    ideas_dic['challenges'] = get_featured_challenges()
    return ideas_dic


def idea_filter(request, phase_pk=None, search_part=None):
    if phase_pk:
        ideas = Idea.objects.filter(
            discarded=False,
            phase_history__current_phase=phase_pk,
            phase_history__current=1).annotate(
                count_like=Count(Case(When(popular_vote__like=True, then=1)))).order_by('-count_like')
    else:
        ideas = Idea.objects.filter(
            Q(authors__user__first_name__icontains=search_part) |
            Q(category__title__icontains=search_part) |
            Q(title__icontains=search_part) |
            Q(summary__icontains=search_part), discarded=False).annotate(
                count_like=Count(Case(When(popular_vote__like=True, then=1)))).order_by('-count_like')

    context = {
        'ideas': ideas,
        'ideas_liked': get_ideas_voted(request, True),
        'ideas_disliked': get_ideas_voted(request, False),
        'ideas_created_by_me': get_ideas_created(request),
        'idea_phase': get_phases_count()
    }

    data = dict()
    if request.is_ajax():
        data['html_idea_list'] = render_to_string('ideax/idea_list_loop.html', context, request=request)
        data['empty'] = 0

        if not ideas:
            data['html_idea_list'] = render_to_string('ideax/includes/empty.html', request=request)
            data['empty'] = 1
        return JsonResponse(data)
    else:
        context['challenges'] = get_featured_challenges()
        context['phase_req'] = phase_pk
        return render(request, 'ideax/idea_list.html', context)


@login_required
def save_idea(request, form, template_name, new=False):
    if request.method == "POST":
        if form.is_valid():
            idea = form.save(commit=False)

            if GOOGLE_RECAPTCHA_URL:
                ''' Begin reCAPTCHA validation '''
                recaptcha_response = request.POST.get('g-recaptcha-response')
                url = GOOGLE_RECAPTCHA_URL
                values = {
                    'secret': GOOGLE_RECAPTCHA_SECRET_KEY,
                    'response': recaptcha_response
                }
                data = urllib.parse.urlencode(values).encode()
                req = urllib.request.Request(url, data=data)
                response = urllib.request.urlopen(req)
                result = json.loads(response.read().decode())
                ''' End reCAPTCHA validation '''
                if not result['success']:
                    messages.error(request, _('Invalid reCAPTCHA. Please try again.'))
                    return render(request, template_name, {'form': form})

            if new:
                idea_autor = UserProfile.objects.get(user=request.user)
                idea.author = idea_autor
                idea.creation_date = timezone.now()
                idea.phase = IdeaPhase.objects.values('id').get(order=1)
                if(idea.challenge):
                    idea.category = idea.challenge.category
                    category_image = Category_Image.get_random_image(idea.challenge.category)
                else:
                    category_image = Category_Image.get_random_image(idea.category)
                if category_image:
                    idea.category_image = category_image.image.url
                idea.save()
                idea.authors.add(idea.author)
                phase_history = Phase_History(current_phase=IdeaPhase.objects.get(order=1),
                                              previous_phase=0,
                                              date_change=timezone.now(),
                                              idea=idea,
                                              author=idea.author,
                                              current=True)
                phase_history.save()
            else:
                idea.save()
            idea.authors.clear()
            idea.authors.add(UserProfile.objects.get(user__email=request.user.email))
            if form.cleaned_data['authors']:
                for author in form.cleaned_data['authors']:
                    idea.authors.add(author)

                msg_context = {"idea":idea,
                                "user":request.user}
                message_menager(msg_context, NotificationType.IDEA_CO_AUTHOR)
                # idea_send_notify(idea=idea, 
                #                 user=request.user, 
                #                 notification_type=NotificationType.IDEA_CO_AUTHOR)
                    
            messages.success(request, _('Idea saved successfully!'))
            audit(request.user.username, get_client_ip(request), 'SAVE_IDEA_OPERATION',
                  Idea.__name__, str(idea.id))
            mark = markdownify(idea.summary + idea.target + idea.oportunity + idea.solution)
            string = BeautifulSoup(mark, 'html.parser')
            usernames = list(set(username.text[1::] for username in
                                 string.findAll('a', {'class': 'direct-mention-link'})))
            user_mentions = []
            for username in usernames:
                user = UserProfile.objects.get(user__username=username)
                user_mentions.append(user.user)
                # idea_send_notify(idea=idea, 
                #                 user=request.user, 
                #                 notification_type=NotificationType.IDEA_MENTION,
                #                 user_mention=user.user)
                
            msg_context = {"idea":idea,
                            "user":request.user,
                            "user_mentions":user_mentions}
            message_menager(msg_context, NotificationType.IDEA_MENTION)

            return redirect('idea_list')

    return render(request, template_name, {'form': form})


@login_required
@permission_required('ideax.add_idea', raise_exception=True)
def idea_new(request):
    queryset = get_authors(request.user.email)
    if request.method == "POST":
        form = IdeaForm(request.POST, authors=queryset)
    else:
        form = IdeaForm(authors=queryset)

    audit(request.user.username, get_client_ip(request), 'CREATE_IDEA_FORM', Idea.__name__, '')

    return save_idea(request, form, 'ideax/idea_new.html', True)


@login_required
@permission_required('ideax.change_idea', raise_exception=True)
def idea_edit(request, pk):
    idea = get_object_or_404(Idea, pk=pk)
    discussion_phase_id = IdeaPhase.objects.values('id').get(order=1)['id']
    if ((request.user.userprofile == idea.author
            and idea.get_current_phase()['current_phase_id'] == discussion_phase_id) or
            request.user.has_perm(settings.PERMISSIONS["MANAGE_IDEA"])):
        queryset = get_authors(request.user.email)
        if request.method == "POST":
            form = IdeaForm(request.POST, instance=idea, authors=queryset)
        else:
            form = IdeaForm(instance=idea, authors=queryset)

        audit(request.user.username, get_client_ip(request), 'EDIT_IDEA_FORM', Idea.__name__, str(idea.id))

        return save_idea(request, form, 'ideax/idea_edit.html')
    else:
        messages.error(request, _('Not supported action'))
        return redirect('index')


@login_required
@permission_required('ideax.delete_idea', raise_exception=True)
def idea_remove(request, pk):
    idea = get_object_or_404(Idea, pk=pk)
    data = dict()
    discussion_phase_id = IdeaPhase.objects.values('id').get(order=1)['id']
    if ((request.user.userprofile == idea.author
            and idea.get_current_phase()['current_phase_id'] == discussion_phase_id)
            or request.user.has_perm(settings.PERMISSIONS["MANAGE_IDEA"])):
        if request.method == 'POST':
            idea.discarded = True
            idea.save()
            data['form_is_valid'] = True
            ideas = get_ideas_init(request)
            data['html_list'] = render_to_string('ideax/idea_list_loop.html', ideas, request=request)
        else:
            context = {'idea': idea}
            data['html_form'] = render_to_string('ideax/includes/partial_idea_remove.html',
                                                 context,
                                                 request=request,)

        audit(request.user.username, get_client_ip(request), 'REMOVE_IDEA_CONFIRMATION', Idea.__name__, str(idea.id))

        return JsonResponse(data)
    else:
        messages.error(request, _('Not supported action'))
        return redirect('index')


@login_required
@permission_required('ideax.add_criterion', raise_exception=True)
def criterion_new(request):
    if request.method == "POST":
        form = CriterionForm(request.POST)
        if form.is_valid():
            criterion = form.save(commit=False)
            criterion.save()
            messages.success(request, _('Criterion saved successfully!'))
            audit(
                request.user.username,
                get_client_ip(request),
                'CREATE_NEW_CRITERION_OPERATION',
                Criterion.__name__,
                str(criterion.id)
            )
            return redirect('criterion_list')
    else:
        form = CriterionForm()

    return render(request, 'ideax/criterion_new.html', {'form': form})


@login_required
def criterion_list(request):
    audit(request.user.username, get_client_ip(request), 'CRITERION_LIST', Criterion.__name__, '')
    return render(request, 'ideax/criterion_list.html', get_criterion_list())


def get_criterion_list():
    return {'criterions': Criterion.objects.all()}


@login_required
@permission_required('ideax.change_criterion', raise_exception=True)
def criterion_edit(request, pk):
    criterion = get_object_or_404(Criterion, pk=pk)
    if request.method == "POST":
        form = CriterionForm(request.POST, instance=criterion)
        if form.is_valid():
            criterion = form.save(commit=False)
            criterion.save()
            messages.success(request, _('Criterion changed successfully!'))
            audit(
                request.user.username,
                get_client_ip(request),
                'EDIT_CRITERION_SAVE',
                Criterion.__name__,
                str(criterion.id)
            )
            return redirect('criterion_list')
    else:
        form = CriterionForm(instance=criterion)

    return render(request, 'ideax/criterion_edit.html', {'form': form})

@login_required
@permission_required('ideax.add_evaluation_parcial', raise_exception=True)
def idea_evaluation_parcial(request, idea_pk):
    valuator = UserProfile.objects.get(user=request.user)
    idea = get_object_or_404(Idea, pk=idea_pk)

    idea_score = 0.0
    divisor = 0
    soma = 0
        
    data = dict()
    if idea.evaluated != EvaluationPhase.DONE.value:
        if request.POST:

            if idea.evaluated == EvaluationPhase.WAITING.value:
                dim = Dimension.objects.filter(active=True)
            elif idea.evaluated == EvaluationPhase.PARCIAL.value:
                evaluations = Evaluation.objects.filter(idea=idea)
                dim = list(map(lambda evaluation: evaluation.dimension, evaluations))

            form_ = EvaluationForm(request.POST, extra=dim)

            evalaluation_completed = True
            if form_.is_valid():

                category_by_dimension = {}
                for i in dim:
                    category_by_dimension[i.pk] = form_.cleaned_data[EvaluationForm.FORMAT_ID % i.pk]

                evalaluation_completed = True
                all_categories_empty = True
                for category in category_by_dimension.values():
                    if category is None:
                        evalaluation_completed = False
                    else:
                        all_categories_empty = False

                if all_categories_empty:
                    data["msg"] = _("To become a more accurate fill, you need to fill in the fill of a dimension.")
                    data["msg_type"] = "warning"
                    data['score_value'] = 0
                    JsonResponse(data)
                else:
                    for i in dim:                        
                        if form_.cleaned_data[EvaluationForm.FORMAT_ID % i.pk] is not None:
                            dimension_value = i.weight * form_.cleaned_data[EvaluationForm.FORMAT_ID % i.pk].value
                            divisor += i.weight
                            soma += dimension_value
                    
                    for i in dim:
                        dimension_value = 0
                        evaluation_list = Evaluation.objects.filter(dimension=i, idea=idea)

                        if form_.cleaned_data[EvaluationForm.FORMAT_ID % i.pk] is not None:
                            dimension_value = i.weight * form_.cleaned_data[EvaluationForm.FORMAT_ID % i.pk].value
                        else:
                            dimension_value = 0

                        idea_dimension = Evaluation.objects.filter(dimension=i, idea=idea)

                        if len(idea_dimension) == 0:
                            evaluation = Evaluation(valuator=valuator,
                                                    idea=idea,
                                                    dimension=i,
                                                    category_dimension=form_.cleaned_data[EvaluationForm.FORMAT_ID % i.pk],
                                                    evaluation_date=timezone.now(),
                                                    dimension_value=dimension_value,
                                                    note=form_.cleaned_data[EvaluationForm.FORMAT_ID_NOTE % i.pk],)
                        else:
                            evaluation = idea_dimension[0]
                            evaluation.valuator = valuator
                            evaluation.evaluation_date = timezone.now()
                            evaluation.category_dimension = form_.cleaned_data[EvaluationForm.FORMAT_ID % i.pk]
                            evaluation.note = form_.cleaned_data[EvaluationForm.FORMAT_ID_NOTE % i.pk]
                            evaluation.dimension_value = dimension_value

                        evaluation.save()
                        audit(
                            request.user.username,
                            get_client_ip(request),
                            'CREATE_EVALUATION_SAVE',
                            Evaluation.__name__,
                            str(evaluation.id)
                        )

                    idea_score = soma/divisor
                    idea.score = idea_score
                    idea.evaluated = EvaluationPhase.PARCIAL.value
                    idea.save()

                    audit(
                        request.user.username,
                        get_client_ip(request),
                        'EDIT_IDEA_EVALUATION_SAVE',
                        Idea.__name__,
                        str(idea.id)
                    )

                    data["msg"] = _("Partial Evaluation saved successfully!")
                    data['score_value'] = idea_score
            else:
                data["msg"] = _("Something went wrong or you're not allowed!")
                return JsonResponse(data, status=500)
        else:
            form_ = EvaluationForm(extra=dim)
            data["msg"] = _("Evaluation saves successfully!")

    data["idea_evaluated"] = idea.evaluated
    return JsonResponse(data)


@login_required
@permission_required('ideax.add_evaluation', raise_exception=True)
def idea_evaluation(request, idea_pk):
    valuator = UserProfile.objects.get(user=request.user)
    idea = get_object_or_404(Idea, pk=idea_pk)

    idea_score = 0.0
    divisor = 0
    soma = 0
        
    data = dict()
    if idea.evaluated != EvaluationPhase.DONE.value:
        if request.POST:

            if idea.evaluated == EvaluationPhase.WAITING.value:
                dim = Dimension.objects.filter(active=True)
            else:
                evaluations = Evaluation.objects.filter(idea=idea)
                dim = list(map(lambda evaluation: evaluation.dimension, evaluations))

            form_ = EvaluationForm(request.POST, extra=dim)

            if form_.is_valid():

                for i in dim:
                    if form_.cleaned_data[EvaluationForm.FORMAT_ID % i.pk] is None:
                        data["msg"] = _("To save a full valuation you need to fill in all the dimensions.")
                        data["msg_type"] = "warning"
                        data['score_value'] = 0
                        return JsonResponse(data)
                    
                for i in dim:
                    idea_dimension = Evaluation.objects.filter(dimension=i, idea=idea)
                    divisor += i.weight

                    if form_.cleaned_data[EvaluationForm.FORMAT_ID % i.pk] is not None:
                        dimension_value = i.weight * form_.cleaned_data[EvaluationForm.FORMAT_ID % i.pk].value
                        soma += dimension_value

                    if len(idea_dimension) == 0:
                        evaluation = Evaluation(valuator=valuator,
                                                idea=idea,
                                                dimension=i,
                                                category_dimension=form_.cleaned_data[EvaluationForm.FORMAT_ID % i.pk],
                                                evaluation_date=timezone.now(),
                                                dimension_value=i.weight * form_.cleaned_data[EvaluationForm.FORMAT_ID % i.pk].value,
                                                note=form_.cleaned_data[EvaluationForm.FORMAT_ID_NOTE % i.pk],)
                    else:
                        evaluation = idea_dimension[0]
                        evaluation.valuator = valuator
                        evaluation.evaluation_date = timezone.now()
                        evaluation.category_dimension = form_.cleaned_data[EvaluationForm.FORMAT_ID % i.pk]
                        evaluation.note = form_.cleaned_data[EvaluationForm.FORMAT_ID_NOTE % i.pk]
                        evaluation.dimension_value = i.weight * form_.cleaned_data[EvaluationForm.FORMAT_ID % i.pk].value

                    evaluation.save()
                    audit(
                        request.user.username,
                        get_client_ip(request),
                        'CREATE_EVALUATION_SAVE',
                        Evaluation.__name__,
                        str(evaluation.id)
                    )

                idea_score = soma/divisor
                idea.score = idea_score
                idea.evaluated = EvaluationPhase.DONE.value
                idea.save()

                msg_context = {"idea":idea,
                               "user":idea.author.user}
                message_menager(msg_context, NotificationType.EVALUATION)

                # idea_notify_email(idea=idea, 
                #                   user=idea.author.user, 
                #                   notification_type=NotificationType.EVALUATION)
                
                audit(
                    request.user.username,
                    get_client_ip(request),
                    'EDIT_IDEA_EVALUATION_SAVE',
                    Idea.__name__,
                    str(idea.id)
                )

                data["msg"] = _("Evaluation saves successfully!")
                data['score_value'] = idea_score
            else:
                data["msg"] = _("Something went wrong or you're not allowed!")
                return JsonResponse(data, status=500)
        else:
            form_ = EvaluationForm(extra=dim)
            data["msg"] = _("Evaluation saves successfully!")
    
    data["idea_evaluated"] = idea.evaluated
    return JsonResponse(data)


@login_required
@permission_required('ideax.delete_criterion', raise_exception=True)
def criterion_remove(request, pk):
    criterion = get_object_or_404(Criterion, pk=pk)
    criterion.delete()
    messages.success(request, _('Criterion removed successfully!'))
    audit(request.user.username, get_client_ip(request), 'REMOVE_CRITERION_SAVE', Criterion.__name__, str(pk))
    return redirect('criterion_list')


@login_required
@permission_required('ideax.add_popular_vote', raise_exception=True)
def like_popular_vote(request, pk):
    user = UserProfile.objects.get(user=request.user)
    vote = Popular_Vote.objects.filter(voter=user, idea__pk=pk)

    idea_ = Idea.objects.get(pk=pk)
    like_boolean = request.path.split("/")[3] == "like"

    if vote.count() == 0:
        like = Popular_Vote(like=like_boolean, voter=user, voting_date=timezone.now(), idea=idea_)
        like.save()

        audit(request.user.username, get_client_ip(request), 'LIKE_SAVE', Popular_Vote.__name__, str(like.id))
    else:
        if vote[0].like == like_boolean:
            audit(
                request.user.username,
                get_client_ip(request),
                'DISLIKE_SAVE',
                Popular_Vote.__name__,
                str(vote[0].id)
            )
            vote.delete()
            like_boolean = None
        else:
            vote.update(like=like_boolean)

    if like_boolean:
        msg_context = {"idea":idea_,
                "user":request.user}
        message_menager(msg_context, NotificationType.LIKE)

    data = dict()
    data['qtde_votes_likes'] = idea_.count_likes()
    data['qtde_votes_dislikes'] = idea_.count_dislikes()
    data['class'] = like_boolean

    return JsonResponse(data)


@login_required
def get_ideas_voted(request, vote):
    user = UserProfile.objects.get(user=request.user)
    ideas_voted = []
    if request.user.is_authenticated:
        ideas_voted = Popular_Vote.objects.filter(like=vote, voter=user).values_list('idea_id', flat=True)

    return ideas_voted


@login_required
def get_ideas_created(request):
    user = UserProfile.objects.get(user=request.user)
    ideas_created = []
    if request.user.is_authenticated:
        ideas_created = Idea.objects.filter(author=user).values_list('id', flat=True)

    return ideas_created


@login_required
@permission_required('ideax.add_phase_history', raise_exception=True)
def change_idea_phase(request, pk, new_phase):
    idea = Idea.objects.get(pk=pk)
    phase = IdeaPhase.objects.get(pk=new_phase)
    if phase is not None:
        phase_history_current = Phase_History.objects.get(idea=idea, current=True)
        phase_history_current.current = False
        phase_history_current.save()
        
        phase_history_new = Phase_History(current_phase_id=phase.id,
                                          previous_phase=phase_history_current.current_phase.id,
                                          date_change=timezone.now(),
                                          idea=idea,
                                          author=UserProfile.objects.get(user=request.user),
                                          current=True)
        phase_history_new.save()
        audit(
            request.user.username,
            get_client_ip(request),
            'CHANGE_PHASE_SAVE',
            phase.name,
            str(phase_history_new.id)
        )
        messages.success(request, _('Phase change successfully!'))
        context = {}
        context['idea'] = idea
        context['phase'] = phase.name
        
        msg_context = {"idea":idea,
                        "user":request.user,
                        "new_phase": phase.name}
        message_menager(msg_context, NotificationType.PHASE)

        # idea_notify_email(idea=idea, 
        #                 user=request.user, 
        #                 notification_type=NotificationType.PHASE, 
        #                 new_phase=phase.name)
        
    return redirect('index')


def sort_timeline(timeline_list, timeline_evaluation):
    if timeline_evaluation:
        for i in range(len(timeline_list)):
            if timeline_evaluation.evaluation_date < timeline_list[i].date_change:
                timeline_list.insert(i, timeline_evaluation)
                break
            elif (i == len(timeline_list)-1):
                timeline_list.insert(len(timeline_list)+1, timeline_evaluation)
    return timeline_list

def __define_user_comments_profile(user):
    groups = user.groups.all()
    for group in groups:
        if group.name == "Gerencial":
            return UserEditCommentsProfile.MANAGER.value
    return UserEditCommentsProfile.PARTIAL.value

@login_required
def idea_detail(request, pk):
    idea = get_object_or_404(Idea, pk=pk, discarded=False)
    timeline_phase_history = idea.phase_history_set.all()
    timeline_evaluation = idea.evaluation_set.last()
    user = request.user
    data = dict()
    isfollow = FollowHelper.isfollow(user, idea)
   
    data["idea"] = idea
    data["idea_id"] = idea.pk
    data["authors"] = idea.authors.all()
    data["creation_date"] = idea.creation_date.strftime("%d/%m/%Y")
    data["timeline"] = sort_timeline(list(timeline_phase_history), timeline_evaluation)
    data["idea_phase"] = get_phases_count()
    data["current_phase"] = Phase_History.objects.get(idea=idea, current=True)
    data["comments"] = idea.comment_set.filter(deleted=False)
    data["comments_edit_permision"] = __define_user_comments_profile(user)
    if data["comments_edit_permision"] == UserEditCommentsProfile.PARTIAL.value:
        data["comments_id_list"] = CommentsHelper.comments_id_user(user,data["comments"])

    same_author = is_same_author(user, idea)
    data["same_author"] = same_author
    if same_author == False:
        data["isfollow"] = isfollow
        data["follow"] = _("Follow")
        data["following"] = _("Following")

    relationship = RelationShipHelper.get_relationship(idea)
    data["relationship"] = relationship
    data["relationship_len"] = len(relationship)

    data["idea_raw"] = RelationShipHelper.get_relationship_raw(idea)
    data["detail_text"] = _("Details...")
    
    initial = collections.OrderedDict()
    form_ = None

    update_evaluation_phase(idea)
    
    idea_evaluation=idea.evaluation_set.all().order_by('dimension__id')

    if idea.evaluated == EvaluationPhase.DONE.value or idea.evaluated == EvaluationPhase.PARCIAL.value:
        for i in idea_evaluation:
            initial[EvaluationForm.FORMAT_ID % i.dimension.pk] = i
        form_ = EvaluationForm(initial=initial)
    else:
        form_ = EvaluationForm(extra=Dimension.objects.filter(active=True))
    
    data["form_evaluation"] = None if not form_.fields else form_
    data["evaluation_detail"] = initial

    try:
        data["popular_vote"] = idea.popular_vote_set.get(voter=request.user.userprofile).like
    except Popular_Vote.DoesNotExist:
        pass

    data["idea_evaluated"] = idea.evaluated
    return render(request, 'ideax/idea_detail.html', data)


@login_required
@permission_required('ideax.add_comment', raise_exception=True)
def post_comment(request):
    if not request.user.is_authenticated:
        return JsonResponse({'msg': _("You need to log in to post new comments.")}, status=500)

    raw_comment = request.POST.get('commentContent', None)
    parent_id = request.POST.get('parentId', None)
    author = UserProfile.objects.get(user=request.user)
    idea_id = request.POST.get('ideiaId', None)

    if ProfanityCheck.wordcheck().search_badwords(raw_comment):
        return JsonResponse({'msg': _("Please check your message it has inappropriate content.")}, status=500)

    if not raw_comment:
        return JsonResponse({'msg': _("You have to write a comment.")}, status=500)

    if not parent_id:
        parent_object = None
    else:
        parent_object = Comment.objects.get(id=parent_id)

    idea = Idea.objects.get(id=idea_id)

    comment = Comment(author=author,
                      raw_comment=mistune.markdown(raw_comment),
                      parent=parent_object,
                      idea=idea,
                      date=timezone.now(),
                      comment_phase=idea.get_current_phase()['current_phase_id'],
                      ip=get_ip(request))

    comment.save()
    
    msg_context = {"idea":idea,
                    "user":request.user}
    message_menager(msg_context, NotificationType.COMMENT)

    audit(request.user.username, get_client_ip(request), 'COMMENT_SAVE', Comment.__name__, comment.log_msg())
    return JsonResponse({"msg": _("Your comment has been posted.")})

@login_required
def put_idea_comment(request, pk):
    if request.method == "PUT": 
        raw_text = json.loads(request.body)
        msg = check_comment(raw_text['text'])
        if msg != None:
            return JsonResponse({'msg': msg}, status=500) 
        CommentsHelper.update_comment(request, pk, raw_text['text'])
        return JsonResponse({"msg": _("Comment updated.")})

@login_required     
def idea_comments(request, pk):
    data = dict()
    comments = Comment.objects.filter(idea__id=pk, deleted=False)
    comments_id_list = ""
    profile = __define_user_comments_profile(request.user)

    if profile == UserEditCommentsProfile.PARTIAL.value:
        comments_id_list = CommentsHelper.comments_id_user(request.user, comments)

    data['html_list'] = render_to_string('ideax/includes/partial_comments.html',
                                         {"comments": comments,
                                         "comments_edit_permision": profile,
                                         "comments_id_list": comments_id_list, 
                                         "idea_id": pk})
    return JsonResponse(data)

@login_required
def delete_idea_comment(request, pk):
    if request.method == "DELETE":
        CommentsHelper.delete_comment(request, pk)
    return JsonResponse({"msg": _("Comment deleted with success.")})

def idea_detail_pdf(request, idea_id):
    idea = Idea.objects.get(pk=idea_id)
    data = dict()
    initial = collections.OrderedDict()
    data['idea'] = idea
    for i in idea.evaluation_set.all().order_by('dimension__id'):
        initial[EvaluationForm.FORMAT_ID % i.dimension.pk] = i

    data['evaluation_detail'] = initial
    audit(request.user.username, get_client_ip(request), 'REPORT_GENERATE', Idea.__name__, str(idea.id))
    return render(request, 'ideax/ftec.html', data)
    # pdf_file = generate_pdf_report('ideax/ftec.html', request.build_absolute_uri(), data)
    # response = HttpResponse('pdf_file', content_type='text/plain')
    # response['Content-Disposition'] = 'filename="idea_report.txt"'
    # return response


def get_featured_challenges():
    return Challenge.objects.filter(active=True).exclude(discarted=True)


@login_required
def challenge_detail(request, challenge_pk):
    challenge = get_object_or_404(Challenge, pk=challenge_pk)
    return render(request, 'ideax/challenge_detail.html', {
        'challenge': challenge,
        'ideas': challenge.idea_set.filter(discarded=False),
    })


@login_required
@permission_required('ideax.add_challenge', raise_exception=True)
def challenge_new(request):
    form = ChallengeForm()
    if request.method == "POST":
        form = ChallengeForm(request.POST, request.FILES)

        if form.is_valid():
            # path  = file_upload(request)
            challenge = form.save()
            challenge.author = UserProfile.objects.get(user=request.user)
            challenge.creation_date = timezone.now()
            challenge.save()
            messages.success(request, _('Challenge saved successfully!'))
            return redirect('challenge_list')
    return render(request, 'ideax/challenge_new.html', {'form': form})


@login_required
@permission_required('ideax.change_challenge', raise_exception=True)
def challenge_edit(request, challenge_pk):
    challenge = get_object_or_404(Challenge, pk=challenge_pk)

    if request.method == "POST":
        form = ChallengeForm(request.POST, request.FILES, instance=challenge)

        if form.is_valid():
            edit_challenge = form.save()
            edit_challenge.creation_date = challenge.creation_date
            edit_challenge.author = challenge.author
            edit_challenge.pk = challenge.pk
            edit_challenge.save()
            messages.success(request, _('Challenge saved successfully!'))
            return redirect('challenge_list')
    else:
        form = ChallengeForm(instance=challenge)

    return render(request, 'ideax/challenge_edit.html', {'form': form})


# TODO: Refactor, unused code
def file_upload(request):
    myfile = request.FILES['image']
    fs = FileSystemStorage()
    filename = fs.save(myfile.name, myfile)
    uploaded_file_url = fs.url(filename)
    return uploaded_file_url


@login_required
@permission_required('ideax.delete_challenge', raise_exception=True)
def challenge_remove(request, pk):
    challenge = get_object_or_404(Challenge, pk=pk)
    if request.method == 'GET':
        challenge.discarted = True
        challenge.save()
        messages.success(request, _('Challenge removed successfully!'))
    else:
        messages.error(request, _('Not supported action'))
    return challenge_list(request)


@login_required
def challenge_list(request):
    if (request.user.has_perm(settings.PERMISSIONS["MANAGE_IDEA"])):
        challenges = Challenge.objects.filter(discarted=False)
    else:
        challenges = get_featured_challenges()

    return render(request, 'ideax/challenge_list.html', {'challenges': challenges, 'actives': get_active_count()})


def get_active_count():
    cursor = connection.cursor()
    cursor.execute('''select count(*) as qtd from ideax_challenge where active = True and discarted = False''')
    data_active = cursor.fetchall()
    cursor.execute('''select count(*) as qtd from ideax_challenge where active = False and discarted = False''')
    data_inactive = cursor.fetchall()
    actives = dict()
    actives['active'] = data_active[0][0]
    actives['inactive'] = data_inactive[0][0]

    return actives


def challenge_filter(request, status=None):
    if status == 0:
        status = True
    else:
        status = False
    challenges = Challenge.objects.filter(
            discarted=False,
            active=status)

    context = {
        'challenges': challenges,
    }

    data = dict()
    if request.is_ajax():
        data['html_challenge_list'] = render_to_string('ideax/challenge_list_loop.html', context, request=request)
        data['empty'] = 0
        if not challenges:
            data['html_challenge_list'] = render_to_string('ideax/includes/empty_challenge.html', request=request)
            data['empty'] = 1
        return JsonResponse(data)
    else:
        context['challenges'] = get_featured_challenges()
        context['actives'] = get_active_count()
        return render(request, 'ideax/challenge_list.html', context)


@login_required
def report_ideas(request):
    if (request.user.has_perm(settings.PERMISSIONS["MANAGE_IDEA"])):
        csv_path = 'RELATORIO_IDEIAS.csv'
        cursor = connection.cursor()
        cursor.execute('''select i.id as id_ideia ,
           i.title as titulo,
           i.score as pontuacao,
           au.username as usuario,
           ic.title as categoria,
           sum(case when pv.`like` = 1 then 1 else 0 end) as qtde_likes,
           sum(case when pv.`like` = 0 then 1 else 0 end) as qtde_dislikes,
           (CASE
                WHEN ph.current_phase = 1 THEN 'Discussao'
                WHEN ph.current_phase = 2 THEN 'Avaliacao'
                WHEN ph.current_phase = 3 THEN 'Ideacao'
                WHEN ph.current_phase = 4 THEN 'Aprovacao'
                WHEN ph.current_phase = 5 THEN 'Evolucao'
                WHEN ph.current_phase = 6 THEN 'Feita'
                WHEN ph.current_phase = 7 THEN 'Arquivada'
                WHEN ph.current_phase = 8 THEN 'Pausada' ELSE 0 END) as fase,
           (select count(*) from ideax_comment where idea_id = i.id) as qtde_comentarios
                from ideax_idea i inner join ideax_popular_vote pv on i.id = pv.idea_id
                inner join ideax_phase_history ph on i.id = ph.idea_id
                inner join ideax_category ic on i.category_id = ic.id
                inner join users_userprofile iu on i.author_id = iu.id
                inner join auth_user au on au.id = iu.user_id
            where ph.current = 1 and i.discarded = 0
            group by i.id, ph.current_phase''')
        data = cursor.fetchall()

        with open(csv_path, 'w', newline='') as f_handle:
            writer = csv.writer(f_handle)
            header = [
                'id_ideia',
                'titulo',
                'pontuacao',
                'usuario',
                'categoria',
                'qtde_likes',
                'qtde_dislikes',
                'fase',
                'qtde_comentarios',
            ]
            writer.writerow(header)
            for row in data:
                writer.writerow(row)

        response = StreamingHttpResponse(open(csv_path), content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=' + csv_path
        return response

    return redirect('index')


@login_required
@permission_required('ideax.add_idea', raise_exception=True)
def idea_new_from_challenge(request, challenge_pk):
    queryset = get_authors(request.user.email)
    challenge = get_object_or_404(Challenge, pk=challenge_pk)
    form = IdeaForm(initial={'challenge': challenge, 'category': challenge.category}, authors=queryset)
    audit(request.user.username, get_client_ip(request), 'CREATE_IDEA_FORM_FROM_MISSION', Idea.__name__, '')
    return save_idea(request, form, 'ideax/idea_new.html', True)


@login_required
def markdown_uploader(request):
    """
    Makdown image upload for locale storage
    and represent as json to markdown editor.
    """
    if request.method == 'POST' and request.is_ajax():
        if 'markdown-image-upload' in request.FILES:
            image = request.FILES['markdown-image-upload']
            image_types = [
                'image/png', 'image/jpg',
                'image/jpeg', 'image/pjpeg', 'image/gif'
            ]
            if image.content_type not in image_types:
                data = json.dumps({
                    'status': 405,
                    'error': _('Bad image format.')
                }, cls=LazyEncoder)
                return HttpResponse(
                    data, content_type='application/json', status=405)

            if image._size > settings.MAX_IMAGE_UPLOAD_SIZE:
                to_mb = settings.MAX_IMAGE_UPLOAD_SIZE / (1024 * 1024)
                data = json.dumps({
                    'status': 405,
                    'error': _('Maximum image file is %(size) MB.') % {'size': to_mb}
                }, cls=LazyEncoder)
                return HttpResponse(
                    data, content_type='application/json', status=405)

            img_uuid = "{0}-{1}".format(uuid.uuid4().hex[:10], image.name.replace(' ', '-'))
            tmp_file = os.path.join(settings.MARTOR_UPLOAD_PATH, img_uuid)
            def_path = default_storage.save(tmp_file, ContentFile(image.read()))
            img_url = os.path.join(settings.MEDIA_URL, def_path)

            data = json.dumps({
                'status': 200,
                'link': img_url,
                'name': image.name
            })
            return HttpResponse(data, content_type='application/json')
        return HttpResponse(_('Invalid request!'))
    return HttpResponse(_('Invalid request!'))


def idea_search(request):
    return idea_filter(request, search_part=request.POST.get('seach_filter', None))


def user_profile_page(request):
    return render(request, 'ideax/user_profile.html')


def get_authors(removed_author):
    return UserProfile.objects.filter(user__is_staff=False) \
        .exclude(user__email__isnull=True) \
        .exclude(user__email__exact='') \
        .exclude(user__email=removed_author)


@login_required
@permission_required('ideax.add_ideaphase', raise_exception=True)
def ideaphase_new(request):
    if request.method == "POST":
        form = IdeaPhaseForm(request.POST)
        if form.is_valid():
            ideaphase = form.save()
            ideaphase.save()
            messages.success(request, _('Idea Phase saved successfully!'))
            audit(request.user.username, get_client_ip(request), 'CREATE_IDEA_PHASE', IdeaPhase.__name__, ideaphase.id)
            return redirect('ideaphase_list')
    else:
        form = IdeaPhaseForm()
    return render(request, 'ideax/ideaphase_new.html', {'form': form})


@login_required
def ideaphase_list(request):
    audit(request.user.username, get_client_ip(request), 'IDEA_PHASE_LIST', IdeaPhase.__name__, '')
    return render(request, 'ideax/ideaphase_list.html', get_ideaphase_list())


def get_ideaphase_list():
    return {'ideaphase_list': IdeaPhase.objects.all()}


@login_required
@permission_required('ideax.change_ideaphase', raise_exception=True)
def ideaphase_edit(request, pk):
    ideaphase = get_object_or_404(IdeaPhase, pk=pk)
    if request.method == "POST":
        form = IdeaPhaseForm(request.POST, instance=ideaphase)
        if form.is_valid():
            ideaphase = form.save(commit=False)
            ideaphase.save()
            messages.success(request, _('Idea Phase changed successfully!'))
            audit(
                request.user.username,
                get_client_ip(request),
                'EDIT_IDEA_PHASE__SAVE',
                IdeaPhase.__name__,
                str(ideaphase.id)
            )
            return redirect('ideaphase_list')
    else:
        form = IdeaPhaseForm(instance=ideaphase)

    return render(request, 'ideax/ideaphase_edit.html', {'form': form})


@login_required
@permission_required('ideax.delete_ideaphase', raise_exception=True)
def ideaphase_remove(request, pk):
    ideaphase = get_object_or_404(IdeaPhase, pk=pk)
    ideaphase.delete()
    messages.success(request, _('Idea Phase removed successfully!'))
    audit(request.user.username, get_client_ip(request), 'REMOVE_IDEA_PHASE_SAVE', IdeaPhase.__name__, str(pk))
    return redirect('ideaphase_list')

@login_required
def idea_follow(request):
    if request.method == "POST":
        raw_text = json.loads(request.body)   
        action = raw_text['action']
        idea_id = raw_text['idea_id']
        idea = Idea.objects.get(id=idea_id)

        if action == "follow":
            FollowHelper.follow(user=request.user, idea=idea)
        else:
            FollowHelper.unfollow(user=request.user, idea=idea)

        return JsonResponse({"msg": "success"})

@login_required
def idea_related(request):
    if request.method == "POST":
        raw_text = json.loads(request.body)
        search_part = raw_text['search_part']
        ideas = []
        if len(search_part) >= 3 or search_part.isdigit():
            idea = Idea.objects.get(pk=raw_text['idea_id'])
            ideas = RelationShipHelper.search_ideas(search_part, idea)
            process_result = "success"
            msg = ""
        else:
            process_result = "error"
            msg = _("The search query must contain at least three characters")

    return JsonResponse({"ideas": ideas, "msg": msg, "process_result": process_result})
 
@login_required
def idea_relationship(request):
    if request.method == "POST":
        raw_text = json.loads(request.body)
        action = raw_text['action']
        idea = Idea.objects.get(pk=raw_text['idea_id'])
        idea_related = Idea.objects.get(pk=raw_text['idea_id_related'])
        if action == "relation":
            RelationShipHelper.relate(idea, idea_related)
            msg = _("Inclusion of the relationship of the successful idea.")
            process_result = "success"

            msg_context = {"idea":idea,
                            "user":idea.author.user,
                            "idea_related": idea_related}
            message_menager(msg_context, NotificationType.RELATIONSHIP)
            
            # idea_notify_email(idea=idea, 
            #                     user=idea.author.user, 
            #                     notification_type=NotificationType.RELATIONSHIP, 
            #                     idea_related=idea_related)
            # idea_notify_email(idea=idea_related, 
            #                  user=idea_related.author.user, 
            #                  notification_type=NotificationType.RELATIONSHIP, 
            #                  idea_related=idea)
        elif action == "unrelation":
            RelationShipHelper.unrelate(idea, idea_related)
            msg = _("Deletion of relationship from successful idea")
            process_result = "error"

        relations = RelationShipHelper.get_relationship(idea)
 
    return JsonResponse({"msg": msg, "relations": relations, "process_result": process_result})


# def email_notification(request, idea, username, email, notification):
#     subject = 'Assunto'
#     message = 'mensagem'

#     ctx = {
#     'idea': idea.title,
#     'username': username.username,
#     'notification': notification,
#     }

#     message = render_to_string('ideax/email_notification.html', ctx)

#     email = EmailMessage(subject=subject, body=message, to=[email])
#     email.content_subtype = "html"
#     email.send()


__all__ = [
    'category_edit', 'category_list', 'category_new', 'category_remove',
    'category_image_edit', 'category_image_list', 'category_image_new', 'category_image_remove',
    'get_term_of_user', 'accept_use_term',
    'get_valid_use_term', 'save_use_term', 'use_term_detail', 'use_term_edit', 'use_term_list',
    'use_term_new', 'use_term_remove',
    'dimension_new', 'dimension_list', 'dimension_edit', 'dimension_remove',
]