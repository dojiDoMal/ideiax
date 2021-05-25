import os
from pathlib import Path

from decouple import config, Csv
from dj_database_url import parse as dburl

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))).parent.parent

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv())

GOOGLE_RECAPTCHA_SECRET_KEY = config('GOOGLE_RECAPTCHA_SECRET_KEY', default='')

GOOGLE_RECAPTCHA_URL = config('GOOGLE_RECAPTCHA_URL', default='')

# Application definition

SHARED_APPS = [    
    'ideax.tenant',
]

TENANT_APPS = [    
    # The following Django contrib apps must be in TENANT_APPS
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'ideax.ideax',
    'ideax.users',
    'django.contrib.admin',        
    'django.contrib.sessions',
    'django.contrib.messages',
    'notifications',
]

INSTALLED_APPS = [
    'tenant_schemas',  # mandatory, should always be before any django app
    'ideax.users.UserConfig',    
    'ideax.tenant',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'widget_tweaks',
    'ideax.ideax.IdeaxConfig',
    'ideax.administration.AdministrationConfig',
    'mptt',    
    'notifications',
]

TENANT_MODEL = "tenant.Client"

MIDDLEWARE = [    
    'ideax.users.middleware.EmailTenantMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    # 'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'ideax.users.middleware.TenantCookieMiddleware',
]

ROOT_URLCONF = 'ideax.urls'
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'ideax.context_processors.export_vars',
                'ideax.context_processors.notifications_processor',
            ],
        },
    },
]

WSGI_APPLICATION = 'ideax.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

default_dburl = 'sqlite:///' + os.path.join(BASE_DIR, 'db.sqlite3')

#DATABASES = {
#    #'default': config('DATABASE_URL', default=default_dburl, cast=dburl),
#    'default': {
#        'ENGINE': 'tenant_schemas.postgresql_backend',
#        # ..
#    }
#}

DATABASES = {
    'default': {
        'ENGINE': 'tenant_schemas.postgresql_backend',
        'NAME': config('DATABASE_NAME'),
        'USER': config('DATABASE_USER'),
        'PASSWORD': config('DATABASE_PASSWORD'),
        'HOST': config('DATABASE_HOST'),
        'PORT': config('DATABASE_PORT', default=""),            # Set to empty string for default.
    }
}

DATABASE_ROUTERS = (
    'tenant_schemas.routers.TenantSyncRouter',
)
# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_L10N = True
USE_TZ = True
USE_I18N = True

LANGUAGES = (
    ('en', 'English'),
    ('pt-br', 'Português'),
    ('es', 'Español')
)
LOCALE_PATHS = (os.path.join(BASE_DIR, 'locale'),)

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'ideax/static'),
]


LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]

PERMISSIONS = {
    "MANAGE_IDEA": "ideax.manage_idea",
}

GENERAL_USER_GROUP = config('GENERAL_USER_GROUP')

MAX_IMAGE_UPLOAD_SIZE = 5242880  # 5MB
SESSION_COOKIE_AGE = 7200
SESSION_SAVE_EVERY_REQUEST = True
PATH_FILE_INIT_DATA = os.path.join(BASE_DIR, 'docker/') + config('FILE_INIT_DATA', default='')

DJANGO_NOTIFICATIONS_CONFIG = { 'USE_JSONFIELD': True}
SESSION_EXPIRE_AT_BROWSER_CLOSE = True