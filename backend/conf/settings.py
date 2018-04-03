"""
Django settings for backend project.

Generated by 'django-admin startproject' using Django 1.11.4.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
from decimal import Decimal

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BACKEND_ROOT = os.path.join(BASE_DIR, 'backend')
os.sys.path = [BACKEND_ROOT] + os.sys.path


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'sdfbv804jrg23945g890efnvdscviu7ndor8tyh0345hwub')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'webpack_loader',
    'rest_framework',
    'rest_framework.authtoken',
    'oauth2_provider',
    'deux',
    'custom_user',
    'easy_thumbnails',
    'djmoney',
    'avatar',
    'recaptcha',
    'apps.profiles.apps.ProfilesConfig',
    'apps.sales.apps.SalesConfig',
    'apps.lib',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'apps.profiles.middleware.rating_middleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'backend.conf.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BACKEND_ROOT, 'templates')],
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

WSGI_APPLICATION = 'wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',
        'USER': 'postgres',
        'HOST': 'db',
        'PORT': 5432,
    }
}

# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

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

AUTH_USER_MODEL = 'profiles.User'

# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]
STATIC_ROOT = os.path.join(BASE_DIR, 'public')
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


WEBPACK_LOADER = {
    'DEFAULT': {
        'BUNDLE_DIR_NAME': '',
        'STATS_FILE': os.path.join(BASE_DIR, 'webpack-stats.json'),
        'CACHE': not DEBUG
    }
}

THUMBNAIL_ALIASES = {
    'profiles.ImageAsset.file': {
        'thumbnail': {'size': (300, 300), 'crop': ',0'},
        'gallery': {'size': (1000, 700)},
        'notification': {'size': (80, 80)}
    },
    'sales.Product.file': {
        'thumbnail': {'size': (300, 300), 'crop': False},
        'preview': {'size': (500, 500), 'crop': False},
        'notification': {'size': (80, 80)}
    },
    'sales.Revision.file': {
        'preview': {'size': (500, 500), 'crop': False},
        'notification': {'size': (80, 80)}
    },
    '': {}
}

DWOLLA_KEY = 'sUNuwIxg71Pbb1IplwysLTDN7tQZS4qRsN9h6W3RQgEeW3z6W4'
DWOLLA_SECRET = 'fLdkagXI9ECOqkXM7o7afX0mTO8h4yLw4HSMklYCXmVpW84tku'
DWOLLA_FUNDING_SOURCE = 'https://api-sandbox.dwolla.com/funding-sources/fd18e5b7-29f1-4b89-955e-ac271ea3fa9b'

AUTHORIZE_KEY = '497HxDC9yd'
AUTHORIZE_SECRET = '3n69vX6qXA7j248x'

DEFAULT_PROTOCOL = 'https'
DEFAULT_DOMAIN = 'artconomy.vulpinity.com'

SANDBOX_APIS = True

MAX_CHARACTER_COUNT = 30

HIDE_TEST_BROWSER = True

CARD_TEST = True

MIN_PASS_LENGTH = 8

BANNED_USERNAMES = ['artconomy']

MINIMUM_PRICE = Decimal('1.10')
MINIMUM_TURNAROUND = Decimal('.01')

REFUND_FEE = Decimal('2.00')

COUNTRIES_NOT_SERVED = (
  'NK',
  'IR',
  'NG'
)

REST_FRAMEWORK = {
  'DEFAULT_PAGINATION_CLASS': 'apps.lib.middleware.ResizablePagination',
  'PAGE_SIZE': 50,
  'DEFAULT_AUTHENTICATION_CLASSES': (
      'rest_framework.authentication.SessionAuthentication',
  )
}

GR_CAPTCHA_SECRET_KEY = '6LdDkkIUAAAAAL1ekZxQwQD2KnWItTmZi_Zs58sC'

GR_CAPTCHA_PUBLIC_KEY = '6LdDkkIUAAAAAFyNzBAPKEDkxwYrQ3aZdVb1NKPw'
