from decouple import config

from ..django._core import INSTALLED_APPS


INSTALLED_APPS.extend([
    'djcelery',
    'djcelery_email',
])

CELERY_ACCEPT_CONTENT = ['pickle', 'json', 'application/text']
CELERY_BROKER_URL = config('CELERY_BROKER_URL', default='')
