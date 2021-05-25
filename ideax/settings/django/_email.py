from decouple import config


EMAIL_HOST = config('EMAIL_HOST', default='')
EMAIL_PORT = config('EMAIL_PORT', default='')
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=0, cast=bool)
EMAIL_USE_SSL = config('EMAIL_USE_SSL', default=0, cast=bool)

if config('EMAIL_BACKEND', default='') != '':
    EMAIL_BACKEND = config('EMAIL_BACKEND', default='')

if config('DEFAULT_FROM_EMAIL', default='') != '':
    DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL')
