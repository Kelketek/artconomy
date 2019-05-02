"""
Django settings for backend project.

Generated by 'django-admin startproject' using Django 1.11.4.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import json
import os
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
from decimal import Decimal
from sys import argv

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

ALLOWED_HOSTS = ENV_TOKENS.get('ALLOWED_HOSTS', ['artconomy.vulpinity.com', 'localhost'])

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_premailer',
    'haystack',
    'celery_haystack',
    'djcelery_email',
    'webpack_loader',
    'rest_framework',
    'rest_framework.authtoken',
    'custom_user',
    'easy_thumbnails',
    'djmoney',
    'avatar',
    'recaptcha',
    'django_markdown2',
    'django_otp',
    'django_otp.plugins.otp_totp',
    'django_otp.plugins.otp_static',
    # Needed to subclass the model. We don't use email for 2FA since we allow password resets as well.
    'django_otp.plugins.otp_email',
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
    'django_otp.middleware.OTPMiddleware',
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
    os.path.join(BASE_DIR, 'static_resources'),
]
STATIC_ROOT = ENV_TOKENS.get('STATIC_ROOT', os.path.join(BASE_DIR, 'public'))
MEDIA_URL = ENV_TOKENS.get('MEDIA_ROOT', '/media/')
MEDIA_ROOT = ENV_TOKENS.get('MEDIA_ROOT', os.path.join(BASE_DIR, 'media'))

FILE_UPLOAD_DIRECTORY_PERMISSIONS = 0o750
FILE_UPLOAD_PERMISSIONS = 0o644


pack_file_name = 'webpack-stats.json' if DEBUG else 'webpack-stats-saved.json'

WEBPACK_LOADER = {
    'DEFAULT': {
        'BUNDLE_DIR_NAME': '',
        'STATS_FILE': os.path.join(BASE_DIR, pack_file_name),
        'CACHE': not DEBUG
    }
}

THUMBNAIL_ALIASES = {
    'profiles.ImageAsset.file': {
        'thumbnail': {'size': (300, 300), 'crop': ',0'},
        'gallery': {'size': (1000, 700)},
        'notification': {'size': (80, 80)}
    },
    'profiles.ImageAsset.preview': {
        'thumbnail': {'size': (300, 300), 'crop': False},
        'notification': {'size': (80, 80)}
    },
    'sales.Product.file': {
        'thumbnail': {'size': (300, 300), 'crop': False},
        'preview': {'size': (500, 500), 'crop': False},
        'notification': {'size': (80, 80)}
    },
    'sales.Product.preview': {
        'thumbnail': {'size': (300, 300), 'crop': False},
        'notification': {'size': (80, 80)}
    },
    'sales.Revision.file': {
        'preview': {'size': (500, 500), 'crop': False},
        'notification': {'size': (80, 80)}
    },
    'sales.Revision.preview': {
        'thumbnail': {'size': (300, 300), 'crop': False},
        'notification': {'size': (80, 80)}
    },
    '': {}
}

THUMBNAIL_PRESERVE_EXTENSIONS = True

DWOLLA_KEY = ENV_TOKENS.get('DWOLLA_KEY', '')
DWOLLA_SECRET = ENV_TOKENS.get('DWOLLA_SECRET', '')
# Named 'key' here mostly to make sure it gets filtered out of error emails.
DWOLLA_FUNDING_SOURCE_KEY = ENV_TOKENS.get(
    'DWOLLA_FUNDING_SOURCE_KEY', ''
)

AUTHORIZE_KEY = ENV_TOKENS.get('AUTHORIZE_KEY', '')
AUTHORIZE_SECRET = ENV_TOKENS.get('AUTHORIZE_SECRET', '')

DEFAULT_PROTOCOL = ENV_TOKENS.get('DEFAULT_PROTOCOL', 'https')
DEFAULT_DOMAIN = ENV_TOKENS.get('DEFAULT_DOMAIN', 'artconomy.vulpinity.com')
PREMAILER_OPTIONS = ENV_TOKENS.get(
    'PREMAILER_OPTIONS', {'base_url': '{}://{}'.format(DEFAULT_PROTOCOL, DEFAULT_DOMAIN), 'remove_classes': False}
)

EMAIL_BACKEND = ENV_TOKENS.get('EMAIL_BACKEND', 'djcelery_email.backends.CeleryEmailBackend')
CELERY_EMAIL_BACKEND = ENV_TOKENS.get('CELERY_EMAIL_BACKEND', 'sendgrid_backend.SendgridBackend')
DEFAULT_FROM_EMAIL = ENV_TOKENS.get('DEFAULT_FROM_EMAIL', 'Artconomy <notifications@artconomy.com>')
RETURN_PATH_EMAIL = ENV_TOKENS.get('RETURN_PATH_EMAIL', 'support@artconomy.com')
SERVER_EMAIL = DEFAULT_FROM_EMAIL

CELERY_EMAIL_TASK_CONFIG = {
    'rate_limit': '50/m',
}

SENDGRID_API_KEY = ENV_TOKENS.get('SENDGRID_API_KEY')

SANDBOX_APIS = ENV_TOKENS.get('SANDBOX_APIS', True)

SENDGRID_SANDBOX_MODE_IN_DEBUG = SANDBOX_APIS
SENDGRID_ECHO_TO_STDOUT = DEBUG

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

MINIMUM_PRICE = Decimal(ENV_TOKENS.get('MINIMUM_PRICE', '1.10'))
MINIMUM_TURNAROUND = ENV_TOKENS.get('MINIMUM_TURNAROUND', Decimal('.01'))

REFUND_FEE = ENV_TOKENS.get('REFUND_FEE', Decimal('2.00'))

MAILCHIMP_API_KEY = ENV_TOKENS.get('MAILCHIMP_API_KEY', '')

MAILCHIMP_LIST_SECRET = ENV_TOKENS.get('MAILCHIMP_LIST_SECRET', '3d3eca5eea')

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
    ),
}
if not DEBUG:
    REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] = (
        'rest_framework.renderers.JSONRenderer',
    )

GR_CAPTCHA_SECRET_KEY = ENV_TOKENS.get('GR_CAPTCHA_SECRET_KEY', '')

GR_CAPTCHA_PUBLIC_KEY = ENV_TOKENS.get('GR_CAPTCHA_PUBLIC_KEY', '')


LOGGING = None

# Uncomment when tests need debugging, like when bok_choy isn't launching the browser.

# if 'test' in argv:
#     LOGGING = {
#         'version': 1,
#         'disable_existing_loggers': False,
#         'formatters': {
#             'console': {
#                 # exact format is not important, this is the minimum information
#                 'format': '%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
#             },
#         },
#         'handlers': {
#             'console': {
#                 'class': 'logging.StreamHandler',
#                 'formatter': 'console',
#             },
#             'mail_admins': {
#                 'level': 'ERROR',
#                 'class': 'django.utils.log.AdminEmailHandler',
#             }
#         },
#         'loggers': {
#             # root logger
#             'bok_choy': {
#                 'level': 'DEBUG',
#                 'handlers': ['console'],
#             },
#             '': {
#                 'level': 'DEBUG',
#                 'handlers': ['console'],
#             }
#         },
#     }

TESTING = 'test' in argv

if TESTING:
    PASSWORD_HASHERS = [
        'django.contrib.auth.hashers.MD5PasswordHasher',
    ]

if ('test' not in argv) and ('runserver' not in argv):
    LOGGING = {
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
                'level': 'ERROR',
                'handlers': ['console'],
            },
        },
    }

AVATAR_EXPOSE_USERNAMES = False

AVATAR_THUMB_FORMAT = 'PNG'

TELEGRAM_BOT_KEY = ENV_TOKENS.get('TELEGRAM_BOT_KEY', '')
TELEGRAM_BOT_USERNAME = ENV_TOKENS.get('TELEGRAM_BOT_USERNAME', '')

RABBIT_HOST = ENV_TOKENS.get('RABBIT_HOST', 'rabbit')
RABBIT_PORT = ENV_TOKENS.get('RABBIT_PORT', 5672)

CELERY_ALWAYS_EAGER = ENV_TOKENS.get('CELERY_ALWAYS_EAGER', False)

CELERY_BROKER_CONNECTION_RETRY = ENV_TOKENS.get('CELERY_BROKER_CONNECTION_RETRY', True)

CELERYBEAT_SCHEDULE = {
    'run_billing': {
        'task': 'apps.sales.tasks.run_billing',
        'schedule': crontab(minute=0, hour=0),
    },
    'check_transactions': {
        'task': 'apps.sales.tasks.check_transactions',
        'schedule': crontab(minute=30)
    },
    'auto_finalize_run': {
        'task': 'apps.sales.tasks.auto_finalize_run',
        'schedule': crontab(hour=1, minute=0)
    },
    'finalize_transactions': {
        'task': 'apps.sales.tasks.finalize_transactions',
        'schedule': crontab(hour=1, minute=15)
    },
    'remind_sales': {
        'task': 'apps.sales.tasks.remind_sales',
        'schedule': crontab(hour=15, minute=30)
    }
}

ENV_NAME = ENV_TOKENS.get('ENV_NAME', 'dev')

OTP_TOTP_ISSUER = ENV_TOKENS.get('OTP_TOTP_ISSUER', 'Artconomy')

TEST_RUNNER = 'apps.lib.test_resources.NPMBuildTestRunner'

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.whoosh_backend.WhooshEngine',
        'PATH': os.path.join(BASE_DIR, 'whoosh_index'),
    },
}

HAYSTACK_SIGNAL_PROCESSOR = 'celery_haystack.signals.CelerySignalProcessor'
