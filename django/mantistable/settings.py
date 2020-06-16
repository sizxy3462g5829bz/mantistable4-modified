"""
Django settings for stiltool project.

Generated by 'django-admin startproject' using Django 2.2.6.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = os.environ.get('SECRET_KEY', 'hpf%js#5+y!zhm!64!i#g#vqys(nxz(fxv-u-@lu894@z1@erg')  # NOTE: Fake key for development

DEBUG = os.environ.get('DEBUG_MODE', '') != 'False'

ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", '')
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", '')

EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST", '')
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_PASSWORD", '')
EMAIL_PORT = 587

HOST = os.environ.get("HOST", "localhost")
PORT = os.environ.get("PORT", "80")

LAMAPI_HOST = os.environ.get("LAMAPI_HOST", "localhost")
LAMAPI_PORT = os.environ.get("LAMAPI_PORT", "8093")

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "[::1]", "web"]
if HOST not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(HOST)


# Application definition

INSTALLED_APPS = [
    'api.apps.ApiConfig',
    'web.apps.WebConfig',
    'web_api.apps.WebApiConfig',
    'dashboard.apps.DashboardConfig',

    'account.apps.AccountConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    'rest_framework',
    'rest_framework_swagger',
    'crispy_forms',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'mantistable.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [""],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'mantistable.wsgi.application'

REST_FRAMEWORK = { 'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.coreapi.AutoSchema' }

SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'api_key': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization'
        }
    },  # setting to pass token in header
    'USE_SESSION_AUTH': False,
    # set to True if session based authentication needed
    'JSON_EDITOR': True,
    'api_path': 'api/',
    'api_version': 'v0',

    "is_authenticated": False,  # Set to True to enforce user authentication,
    "is_superuser": False,  # Set to True to enforce admin only access
    'unauthenticated_user': 'django.contrib.auth.models.AnonymousUser',
    # unauthenticated user will be shown as Anonymous user in swagger UI.
}

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'djongo',
        'NAME': 'mantistable',
        'HOST': 'mongo',
        'PORT': 27017
    }
}
    
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'


# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# CELERY settings
CELERY_BROKER_URL = 'redis://redis'
# BROKER_URL = 'redis://redis:6379'
CELERY_RESULT_BACKEND = 'redis://redis:6379'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/staticfiles/'
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

STATICFILES_DIRS = [
    'node_modules',
]

CRISPY_TEMPLATE_PACK = 'bootstrap3'

# Account app settings
LOGIN_URL = "/login"
ACCOUNT_SETTINGS = {
    "registration": {
        "redirect": "index",
        "mail_subject": "ToolName Account Activation"
    },
    "login": {
        "redirect": "index",
    },
    "logout": {
        "redirect": "index",
    }
}

# Mantistable settings
# Private resource directory (Domain specific resources)
MANTIS_RES_DIR = os.path.join(BASE_DIR, os.path.join('api', 'resources'))
