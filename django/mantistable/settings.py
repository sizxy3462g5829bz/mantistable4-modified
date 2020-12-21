"""
Django settings for stiltool project.

Generated by 'django-admin startproject' using Django 2.2.6.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os
from .config import Config

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = "mantistable.yml"

config = Config(CONFIG_PATH)


#SECRET_KEY = os.environ.get('SECRET_KEY', 'hpf%js#5+y!zhm!64!i#g#vqys(nxz(fxv-u-@lu894@z1@erg')  # NOTE: Fake key for development
SECRET_KEY = config["mantistable"].get("secretKey", 'hpf%js#5+y!zhm!64!i#g#vqys(nxz(fxv-u-@lu894@z1@erg')

#DEBUG = os.environ.get('DEBUG_MODE', '') != 'False'
DEBUG = config["mantistable"].get("debug", True) != False

#ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", '')
#ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", '')
ADMIN_USERNAME = config["mantistable"]["admin"].get("username", "")
ADMIN_PASSWORD = config["mantistable"]["admin"].get("password", "")

EMAIL_USE_TLS = True
#EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST = config["mantistable"]["smtp"].get("host", "smtp.gmail.com")
#EMAIL_HOST_USER = os.environ.get("EMAIL_HOST", '')
EMAIL_HOST_USER = config["mantistable"]["smtp"].get("user", "")
#EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_PASSWORD", '')
EMAIL_HOST_PASSWORD = config["mantistable"]["smtp"].get("password", "")
EMAIL_PORT = 587

HOST = os.environ.get("HOST", "localhost")
PORT = os.environ.get("PORT", "80")

#LAMAPI_HOST = os.environ.get("LAMAPI_HOST", "localhost")
#LAMAPI_PORT = os.environ.get("LAMAPI_PORT", "8093")
LAMAPI_BACKENDS = config["mantistable"].get("lamapi", {})


ALLOWED_HOSTS = ["localhost", "127.0.0.1", "[::1]", "web", "0.0.0.0", "149.132.176.50", "51.144.177.47", "35.236.42.69"]
if HOST not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(HOST)


# Application definition

INSTALLED_APPS = [
    'api.apps.ApiConfig',
    'web_api.apps.WebApiConfig',
    'dashboard.apps.DashboardConfig',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    'rest_framework',
    'rest_framework_swagger',
    'corsheaders',
    'crispy_forms',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
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
                'dashboard.context.websocket_url'
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
    
# CORS

# TODO: Check this
CORS_ORIGIN_ALLOW_ALL = True
#CORS_ALLOW_CREDENTIALS = True
#CORS_ORIGIN_WHITELIST = [
#    'http://localhost:3000',
#]
#CORS_ORIGIN_REGEX_WHITELIST = [
#    'http://localhost:3000',
#]

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.coreapi.AutoSchema',
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 10
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
CELERY_BROKER_URL = 'redis://mantistable4_redis'
# BROKER_URL = 'redis://redis:6379'
CELERY_RESULT_BACKEND = 'redis://mantistable4_redis:6379'
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
LOGIN_URL = "login"

# Mantistable settings
# Private resource directory (Domain specific resources)
MANTIS_RES_DIR = os.path.join(BASE_DIR, os.path.join('api', 'resources'))
