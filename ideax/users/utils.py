from django.contrib.auth import get_user_model
from django.shortcuts import redirect
from .models import AuthConfiguration


def check_authconfiguration(request):
    if request.user.is_superuser:
        if AuthConfiguration.objects.filter(active=True):
            pass
        else:
            return redirect('users:set-configuration')


def get_auth_configuration():
    return AuthConfiguration.objects.get(active=True)


def disable_auth_configuration(excluded_id):
    AuthConfiguration.objects.exclude(id=excluded_id).update(active=False)


def create_super_user(username, email, password):
    user = get_user_model()
    user.objects.create_superuser(username, email, password)
