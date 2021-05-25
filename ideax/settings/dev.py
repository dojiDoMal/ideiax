from ._base import *


INSTALLED_APPS.append('django_extensions')

# Configurações de E-mail para dev
EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
