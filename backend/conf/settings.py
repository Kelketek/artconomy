"""
Django settings for backend project.

Generated by 'django-admin startproject' using Django 1.11.4.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os

import json

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
from decimal import Decimal

from celery.schedules import crontab

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BACKEND_ROOT = os.path.join(BASE_DIR, 'backend')
os.sys.path = [BACKEND_ROOT] + os.sys.path

with open(os.path.join(BASE_DIR, "..", "settings.json")) as env_file:
    ENV_TOKENS = json.load(env_file)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

ADMINS = ENV_TOKENS.get('ADMINS', [('Fox', 'fox@vulpinity.com')])

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = ENV_TOKENS.get('DJANGO_SECRET_KEY', '')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = ENV_TOKENS.get('DEBUG', True)

ALLOWED_HOSTS = ENV_TOKENS.get('ALLOWED_HOSTS', ['artconomy.vulpinity.com'])

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_premailer',
    'webpack_loader',
    'rest_framework',
    'rest_framework.authtoken',
    'custom_user',
    'easy_thumbnails',
    'djmoney',
    'avatar',
    'recaptcha',
    'apps.profiles.apps.ProfilesConfig',
    'apps.sales.apps.SalesConfig',
    'apps.lib',
    'apps.tg_bot.apps.TGBotConfig'
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

ROOT_URLCONF = 'conf.urls'

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

DATABASES = ENV_TOKENS.get(
    'DATABASES', {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'postgres',
            'USER': 'postgres',
            'HOST': 'db',
            'PORT': 5432,
        }
    }
)

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
TIME_ZONE = ENV_TOKENS.get('TIME_ZONE', 'America/Chicago')
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

STATIC_URL = ENV_TOKENS.get('STATIC_URL', '/static/')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]
STATIC_ROOT = ENV_TOKENS.get('STATIC_ROOT', os.path.join(BASE_DIR, 'public'))
MEDIA_URL = ENV_TOKENS.get('MEDIA_ROOT', '/media/')
MEDIA_ROOT = ENV_TOKENS.get('MEDIA_ROOT', os.path.join(BASE_DIR, 'media'))


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

DWOLLA_KEY = ENV_TOKENS.get('DWOLLA_KEY', '')
DWOLLA_SECRET = ENV_TOKENS.get('DWOLLA_SECRET', '')
DWOLLA_FUNDING_SOURCE = ENV_TOKENS.get(
    'DWOLLA_FUNDING_SOURCE', ''
)

AUTHORIZE_KEY = ENV_TOKENS.get('AUTHORIZE_KEY', '')
AUTHORIZE_SECRET = ENV_TOKENS.get('AUTHORIZE_SECRET', '')

DEFAULT_PROTOCOL = ENV_TOKENS.get('DEFAULT_PROTOCOL', 'https')
DEFAULT_DOMAIN = ENV_TOKENS.get('DEFAULT_DOMAIN', 'artconomy.vulpinity.com')
PREMAILER_OPTIONS = ENV_TOKENS.get(
    'PREMAILER_OPTIONS', {'base_url': '{}://{}'.format(DEFAULT_PROTOCOL, DEFAULT_DOMAIN), 'remove_classes': False}
)

EMAIL_BACKEND = 'djcelery_email.backends.CeleryEmailBackend'
CELERY_EMAIL_BACKEND = ENV_TOKENS.get('CELERY_EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
DEFAULT_FROM_EMAIL = ENV_TOKENS.get('DEFAULT_FROM_EMAIL', 'Artconomy <noreply@artconomy.com>')
SERVER_EMAIL = DEFAULT_FROM_EMAIL

CELERY_EMAIL_TASK_CONFIG = {
    'queue': 'email',
    'rate_limit': '50/m',
}

SANDBOX_APIS = ENV_TOKENS.get('SANDBOX_APIS', True)

MAX_CHARACTER_COUNT = ENV_TOKENS.get('MAX_CHARACTER_COUNT', 30)
MAX_ATTRS = ENV_TOKENS.get('MAX_ATTRS', 10)

PREMIUM_PERCENTAGE_FEE = Decimal(ENV_TOKENS.get('PREMIUM_PERCENTAGE_FEE', '4'))
STANDARD_PERCENTAGE_FEE = Decimal(ENV_TOKENS.get('PREMIUM_PERCENTAGE_FEE', '8'))
PREMIUM_STATIC_FEE = Decimal(ENV_TOKENS.get('PREMIUM_PERCENTAGE_FEE', '.50'))
STANDARD_STATIC_FEE = Decimal(ENV_TOKENS.get('PREMIUM_STATIC_FEE', '.75'))
LANDSCAPE_PRICE = Decimal(ENV_TOKENS.get('PREMIUM_PRICE', '5.00'))
PORTRAIT_PRICE = Decimal(ENV_TOKENS.get('STANDARD_PRICE', '3.00'))

HIDE_TEST_BROWSER = ENV_TOKENS.get('HIDE_TEST_BROWSER', True)

CARD_TEST = ENV_TOKENS.get('CARD_TEST', True)

MIN_PASS_LENGTH = ENV_TOKENS.get('MIN_PASS_LENGTH', 8)

BANNED_USERNAMES = ENV_TOKENS.get('BANNED_USERNAMES', ['artconomy'])

MINIMUM_PRICE = ENV_TOKENS.get('MINIMUM_PRICE', Decimal('1.10'))
MINIMUM_TURNAROUND = ENV_TOKENS.get('MINIMUM_TURNAROUND', Decimal('.01'))

REFUND_FEE = ENV_TOKENS.get('REFUND_FEE', Decimal('2.00'))

COUNTRIES_NOT_SERVED = ENV_TOKENS.get(
    'COUNTRIES_NOT_SERVED',
    (
      'NK',
      'IR',
      'NG'
    )
)

REST_FRAMEWORK = {
  'DEFAULT_PAGINATION_CLASS': 'apps.lib.middleware.ResizablePagination',
  'PAGE_SIZE': 50,
  'DEFAULT_AUTHENTICATION_CLASSES': (
      'rest_framework.authentication.SessionAuthentication',
  )
}

GR_CAPTCHA_SECRET_KEY = ENV_TOKENS.get('GR_CAPTCHA_SECRET_KEY', '')

GR_CAPTCHA_PUBLIC_KEY = ENV_TOKENS.get('GR_CAPTCHA_PUBLIC_KEY', '')

import logging.config

from sys import argv

if 'test' not in argv and 'runserver' not in argv:

    LOGGING_CONFIG = None
    logging.config.dictConfig({
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'console': {
                # exact format is not important, this is the minimum information
                'format': '%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
            },
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'console',
            },
            'mail_admins': {
                'level': 'ERROR',
                'class': 'django.utils.log.AdminEmailHandler',
            }
        },
        'loggers': {
            # root logger
            '': {
                'level': 'WARNING',
                'handlers': ['console', 'mail_admins'],
            },
        },
    })

AVATAR_EXPOSE_USERNAMES = False

AVATAR_THUMB_FORMAT = 'PNG'

TELEGRAM_BOT_KEY = ENV_TOKENS.get('TELEGRAM_BOT_KEY', '')
TELEGRAM_BOT_USERNAME = ENV_TOKENS.get('TELEGRAM_BOT_USERNAME', '')

RABBIT_HOST = ENV_TOKENS.get('RABBIT_HOST', 'rabbit')
RABBIT_PORT = ENV_TOKENS.get('RABBIT_PORT', 5672)

CELERY_ALWAYS_EAGER = ENV_TOKENS.get('CELERY_ALWAYS_EAGER', False)


CELERYBEAT_SCHEDULE = {
    'run_billing': {
        'task': 'apps.sales.tasks.run_billing',
        'schedule': crontab(minute=0, hour=0),
    }
}