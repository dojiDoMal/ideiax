from django.apps import AppConfig
from django.contrib.auth.signals import user_logged_in


class UserConfig(AppConfig):
    name = 'ideax.users'

    def ready(self):
        from .signals import check_user_profile  # noqa

        user_logged_in.connect(check_user_profile)
