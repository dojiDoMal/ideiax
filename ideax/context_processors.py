from decouple import config
from django.conf import settings


def export_vars(request):
    return {
        "PIWIK_URL": config("PIWIK_URL", default=""),
        "PIWIK_ID": config("PIWIK_ID", default=""),
        "DIALOGFLOW_ID": config("DIALOGFLOW_ID", default=""),
        "GOOGLE_RECAPTCHA_PUBLIC_KEY": config("GOOGLE_RECAPTCHA_PUBLIC_KEY", default=""),
        "PERMISSIONS": settings.PERMISSIONS,
        "IDEAX_VERSION": config("IDEAX_VERSION", default=""),
    }


def notifications_processor(request):
    boolnotify = False
    if request.user.is_anonymous:
        return {'notifications': "", 'qtde': 0, 'boolnotify': boolnotify}
    notifications = request.user.notifications.unread()
    if len(notifications) == 0:
        boolnotify = True
    return {'notifications': notifications, 'qtde': len(notifications), 'boolnotify': boolnotify}
