"""
Django settings for bpmLogGenerator project.

Generated by 'django-admin startproject' using Django 3.2.6.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

from pathlib import Path
import os
import sys
import environ
from django.core.management.utils import get_random_secret_key

# Initialise environment variables
env = environ.Env()
environ.Env.read_env()

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Variability function that modify UI element (json) properties
var_func_modify_properties = ["gui_component_status"]

# Database configuration
DB_NAME =       env('DB_NAME')
DB_HOST =       env('DB_HOST')
DB_PORT =       env('DB_PORT')
DB_USER =       env('DB_USER')
DB_PASSWORD =   env('DB_PASSWORD')

# bpmLogGenerator API version
API_VERSION =                               env('API_VERSION')
FRONTEND_PREFIX =                           env('FRONTEND_PREFIX')
PREFIX_SCENARIO =                           env('PREFIX_SCENARIO')
EXPERIMENT_RESULTS_PATH =                   env('EXPERIMENT_RESULTS_PATH')
UI_LOGS_FOLDERNAME =                        env('UI_LOGS_FOLDERNAME')
ADDITIONAL_SCENARIOS_RESOURCES_FOLDERNAME = env('ADDITIONAL_SCENARIOS_RESOURCES_FOLDERNAME')

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = get_random_secret_key()

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework', # 3rd Party Apps
    'rest_framework.authtoken',
    'rest_auth',
    'django.contrib.sites',
    'django_extensions',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'rest_auth.registration',
    'corsheaders',
    'drf_spectacular',
    'drf_spectacular_sidecar',  # required for Django collectstatic discovery
    'categories',
    'categories.editor',
    'private_storage',
    'users', # Local App
    'experiments', # Local App
    'wizard', # Local App
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # Add the corsheaders middleware to the top of the
    # middleware list. The middleware list will already
    # exists and have other items in it.
    'corsheaders.middleware.CorsMiddleware',
]

ROOT_URLCONF = 'bpmloggenerator.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'build', BASE_DIR / 'templates'],#, BASE_DIR / 'venv' / 'Lib' /'allauth' /'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.request',
            ],
        },
    },
]

WSGI_APPLICATION = 'bpmloggenerator.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': DB_NAME,
        'HOST': DB_HOST,
        'PORT': DB_PORT,
        'USER': DB_USER,
        'PASSWORD': DB_PASSWORD,
    }
    # 'default': {
    #     'ENGINE': 'django.db.backends.sqlite3',
    #     'NAME': BASE_DIR / 'db.sqlite3',
    # }
}


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

STATICFILES_DIRS = [
  # Tell Django where to look for React's static files (css, js)
  os.path.join(BASE_DIR, "build/static"),
]

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ========== 3rd Party Apps: Additional functionality ==========
# - Rest Framework

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    # 'DATETIME_FORMAT': "%m/%d/%Y %I:%M%P",
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
}

# - Drsf spectacular

SPECTACULAR_SETTINGS = {
    'TITLE': 'bpmLogGenerator API',
    'DESCRIPTION': 'Automatic generation of sintetic UI log in RPA context introducing variability',
    'VERSION': '1.0.0',
    # OTHER SETTINGS
    'SWAGGER_UI_DIST': 'SIDECAR',  # shorthand to use the sidecar instead
    'SWAGGER_UI_FAVICON_HREF': 'SIDECAR',
    'REDOC_DIST': 'SIDECAR',
    # OTHER SETTINGS
}

# - Private storage

PRIVATE_STORAGE_ROOT = os.path.join(BASE_DIR, "privatefiles")
PRIVATE_STORAGE_AUTH_FUNCTION = 'experiments.permissions.allow_staff'

# Specifies localhost port 3000 where the React
# server will be running is safe to receive requests
# from. All all of this.

 # SECURITY WARNING: don't run with debug turned on in production!

CORS_ALLOWED_ORIGINS = [
  'http://localhost:3000'
]


CSRF_TRUSTED_ORIGINS = [
     "example.com"
]

# Build paths inside the project like this: BASE_DIR / 'subdir'.
# server will be running is safe to receive requests

# Django All Auth config. Add all of this.
#EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = env('EMAIL_HOST')
EMAIL_PORT = 587
# EMAIL_PORT = 465
DEFAULT_FROM_EMAIL = env('EMAIL_HOST_USER')
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = True
# EMAIL_USE_SSL = True
SITE_ID = 1 

AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
)

#django-allauth registraion settings
# ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS =1
ACCOUNT_EMAIL_REQUIRED = True
# ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_LOGIN_ATTEMPTS_LIMIT = 5
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_SESSION_REMEMBER = True
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_UNIQUE_EMAIL = True
OLD_PASSWORD_FIELD_ENABLED = True
ACCOUNT_CONFIRM_EMAIL_ON_GET = True
LOGIN_URL = "canela.lsi.us.es/bpmloggenerator/login"
ACCOUNT_EMAIL_CONFIRMATION_ANONYMOUS_REDIRECT_URL = "canela.lsi.us.es/bpmloggenerator/login"
# 1 day
ACCOUNT_LOGIN_ATTEMPTS_TIMEOUT = 86400

# bpmLogGenerator platform settings
# OS 
# operating_system =sys.platform
# print("Operating system detected: " + operating_system)
# Element specification filename and path separator (depends on OS)
# if "win" in operating_system:
#     sep = "\\"
#     element_trace = "configuration"+sep+"element_trace.json"
# else:
sep = "/"
element_trace = "configuration"+sep+"element_trace_linux.json"
# Function specification filename
function_trace = "configuration"+sep+"function_trace.json"