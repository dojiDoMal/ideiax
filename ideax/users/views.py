from django.contrib import messages
from django.contrib.auth import authenticate, views as auth_views
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _ # noqa
from django.views.generic import CreateView
from django.db.models import Count, Case, When
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from tenant_schemas.utils import get_tenant_model
from ideax.util import get_ip, get_client_ip, audit
from ideax.tenant.utils import set_connection
from .forms import SignUpForm, AuthConfigurationForm, PermissionForm
from ..ideax.models import Popular_Vote, Comment, Idea
from .models import UserProfile, AuthConfiguration
from .utils import get_auth_configuration, disable_auth_configuration


@login_required
def profile(request, username):
    from ..ideax.views import get_ideas_voted
    if request.user.username == username:
        votes = Popular_Vote.objects.filter(voter=request.user.id).values(
            'id').annotate(contador=Count(Case(When(like=True, then=1))))
        comments = Comment.objects.filter(author_id=request.user.id).count()
        filter_user = request.user
        query_ideas = request.user.userprofile.authors.filter(discarded=False)
    else:
        user = UserProfile.objects.filter(user__username=username)
        pk = user[0].id
        votes = Popular_Vote.objects.filter(voter=pk).values(
            'voter_id').annotate(contador=Count(Case(When(like=True, then=1))))
        comments = Comment.objects.filter(author_id=pk).count()
        filter_user = UserProfile.objects.filter(id=pk)[0].user
        query_ideas = UserProfile.objects.filter(id=pk)[0].user.userprofile.authors.filter(discarded=False)
    if not votes:
        getvotes = 0
    else:
        getvotes = votes[0]['contador']
    return render(
        request,
        'users/profile.html',
        {
            'userP': filter_user,
            'ideas': query_ideas,
            'popular_vote': getvotes,
            'comments': comments,
            'username': request.user.username,
            'ideas_liked': get_ideas_voted(request, True),
            'ideas_disliked': get_ideas_voted(request, False)
        }
    )


@login_required
def who_innovates(request):
    data = dict()
    data['ideas'] = Idea.objects.values(
        "author__user__username",
        "author__user__email",
        "author_id"
        ).filter(discarded=False).annotate(qtd=Count('author_id'))

    return render(request, 'users/who_innovates.html', data)


class SignUpView(CreateView):
    form_class = SignUpForm
    success_url = reverse_lazy('index')
    template_name = 'users/sign_up.html'

    def form_invalid(self, form):
        messages.error(self.request, _('Invalid form!'))
        return super().form_invalid(form)

    def form_valid(self, form):
        response = super().form_valid(form)
        username = form.cleaned_data.get('username')
        raw_password = form.cleaned_data.get('password1')
        user = authenticate(username=username, password=raw_password)
        login(self.request, user)
        return response


def login(request):
    if request.method == "POST":
        email = request.POST.get('username', '')
        try:
            validate_email(email)
            hostname = email.split('@')[1]
            tenant_model = get_tenant_model()
            set_connection(request, hostname)
        except ValidationError as error:
            messages.error(request, error.message)
            return redirect('users:login')
        except tenant_model.DoesNotExist:
            messages.error(request, _('Tenant not found'))
            return redirect('users:login')
        except AssertionError:
            messages.error(request, _('Invalid tenant model'))
            return redirect('users:login')

        request.session['client'] = request.tenant.domain_url
    return auth_views.login(request)


@login_required
@permission_required('users.add_authconfiguration', raise_exception=True)
def set_authconfiguration(request, new=False):
    if request.method == "POST":
        form = AuthConfigurationForm(request.POST)
    else:
        form = AuthConfigurationForm()

    audit(request.user.username,
          get_client_ip(request),
          'SET_AUTH_CONFIGURATION',
          AuthConfiguration.__name__, '')
    return save_authconfiguration(request, form, 'configuration/configuration_new.html', True)


def save_authconfiguration(request, form, template_name, new=False):
    if request.method == "POST":
        if form.is_valid():
            auth_configuration = form.save(commit=False)
            auth_configuration.active = True
            auth_configuration.configuration_date = timezone.localtime(timezone.now())
            auth_configuration.configuration_admin_ip = get_ip(request)
            auth_configuration.configuration_admin = request.user.username
            auth_configuration.save()
            disable_auth_configuration(auth_configuration.id)
            messages.success(request, _('Configuration saved successfully!'))

            if new:
                return redirect('use_term_new')
            return redirect('idea_list')

    return render(request, template_name, {'form': form})


@login_required
@permission_required('users.change_authconfiguration', raise_exception=True)
def auth_configuration_edit(request):
    auth_configuration = get_auth_configuration()
    if request.method == "POST":
        form = AuthConfigurationForm(request.POST, instance=auth_configuration)
        if form.is_valid():
            auth_configuration_edited = AuthConfiguration()
            auth_configuration_edited.auth_type = form.cleaned_data['auth_type']
            auth_configuration_edited.host = form.cleaned_data['host']
            auth_configuration_edited.bind_dn = form.cleaned_data['bind_dn']
            auth_configuration_edited.bind_password = form.cleaned_data['bind_password']
            auth_configuration_edited.user_search_base = form.cleaned_data['user_search_base']
            auth_configuration_edited.user_filter = form.cleaned_data['user_filter']
            auth_configuration_edited.active = True
            auth_configuration_edited.configuration_date = timezone.localtime(timezone.now())
            auth_configuration_edited.configuration_admin_ip = get_ip(request)
            auth_configuration_edited.configuration_admin = request.user.username
            auth_configuration_edited.save()
            disable_auth_configuration(auth_configuration_edited.id)
            messages.success(request, _('Configuration saved successfully!'))

            return redirect('idea_list')

    else:
        form = AuthConfigurationForm(instance=auth_configuration)

    audit(
        request.user.username,
        get_client_ip(request),
        'EDIT_AUTH_CONFIGURATION',
        AuthConfiguration.__name__,
        ''
    )

    return save_authconfiguration(request, form, 'configuration/configuration_edit.html', False)


@login_required
@permission_required('auth.change_user', raise_exception=True)
def user_permissions_select(request):
    users = []
    for user in get_user_model().objects.filter(is_superuser=False).prefetch_related('groups').order_by('username'):
        if request.user.username == user.username:
            continue
        temp = {'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email,
        'id': user.id,
        'groups': user.groups.values_list('name', flat=True)}
        users.append(temp)
    return render(request, 'permission/select_user_permission.html', {'users':users})


@login_required
@permission_required('auth.change_user', raise_exception=True)
def user_permissions_edit(request, username):
    if request.user.username == username:
        messages.warning(request, _('User cannot change their own permissions'))
        return redirect('/permission/select/')
    user = get_user_model().objects.filter(username=username)
    if request.method == "POST":
        form = PermissionForm(request.POST, instance=user[0])
        if form.is_valid():
            form.save()
            messages.success(request, _('Profile associated with success'))
        else:
            messages.error(request, _('It is necessary to associate at least one profile'))
    else:
        form = PermissionForm(instance=user[0])
    return render(request, 'permission/edit_user_permission.html', {'form':form, 'usuario':user[0]})
