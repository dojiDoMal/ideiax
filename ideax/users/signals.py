from django.conf import settings
from django.contrib.auth.models import Group

from .models import UserProfile


def check_user_profile(sender, request, user, **kwargs):
    try:
        user_profile = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist:
        user_profile = UserProfile()
        user_profile.user = user
        user_profile.save()
        user.groups.add(Group.objects.get(name=settings.GENERAL_USER_GROUP))
