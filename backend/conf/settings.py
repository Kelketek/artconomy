"""
Django settings for backend project.

Generated by 'django-admin startproject' using Django 1.11.4.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import json
import logging
import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
from base64 import decodebytes
from decimal import Decimal
from pathlib import Path
from sys import argv
from typing import Any

from celery.exceptions import ImproperlyConfigured
from celery.schedules import crontab
from moneyed import Money

TESTING = "test" in argv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BACKEND_ROOT = os.path.join(BASE_DIR, "backend")
os.sys.path = [BACKEND_ROOT] + os.sys.path

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

ADMINS = os.environ.get("ADMINS", [("Fox", "fox@artconomy.com")])


class UNSET:
    """
    To be used if we need to throw should a setting not be set.
    """

    def __init__(self):
        raise TypeError("This is to be used as a constant, not initialized.")


def get_env(name: str, default: Any, unpack=False) -> Any:
    if name not in os.environ:
        if default is UNSET:
            raise ImproperlyConfigured(f"Environment variable ${name} is missing.")
        return default
    var = os.environ.get(name)
    if unpack:
        var = decodebytes(var.encode("ascii"))
        return json.loads(var)
    return var


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = get_env("DJANGO_SECRET_KEY", UNSET)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = bool(int(get_env("DEBUG", 1)))

ALLOWED_HOSTS = get_env(
    "ALLOWED_HOSTS", ["artconomy.vulpinity.com", "localhost"], unpack=True
)
if TESTING or DEBUG:
    ALLOWED_HOSTS += ["*"]

CSRF_TRUSTED_ORIGINS = [f"https://{source}" for source in ALLOWED_HOSTS]

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.sites",
    "django.contrib.sitemaps",
    "static_sitemaps",
    "daphne",
    "django.contrib.staticfiles",
    "django_premailer",
    "djcelery_email",
    "django_vite",
    "rest_framework",
    "adrf",
    "rest_framework.authtoken",
    "custom_user",
    "easy_thumbnails",
    "djmoney",
    "avatar",
    "recaptcha",
    "reversion",
    "hitcount",
    "django_markdown2",
    "channels",
    "django_otp",
    "django_otp.plugins.otp_totp",
    "django_otp.plugins.otp_static",
    # Needed to subclass the model. We don't use email for 2FA since we allow password
    # resets as well.
    "django_otp.plugins.otp_email",
    "apps.profiles.apps.ProfilesConfig",
    "apps.sales.apps.SalesConfig",
    "apps.lib.apps.LibConfig",
    "apps.tg_bot.apps.TGBotConfig",
    "django_cleanup.apps.CleanupConfig",
    "apps.discord_bot.apps.DiscordBotConfig",
]


MIDDLEWARE = [
    "csp.middleware.CSPMiddleware",
    "apps.lib.middleware.GlobalRequestMiddleware",
    "apps.lib.middleware.VersionShimMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "apps.lib.middleware.MonkeyPatchMiddleWare",
    "django_otp.middleware.OTPMiddleware",
    "apps.lib.middleware.IPMiddleware",
    "apps.profiles.middleware.RatingMiddleware",
    "apps.profiles.middleware.SubjectMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "conf.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BACKEND_ROOT, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "apps.lib.context_processors.settings_context",
            ],
        },
    },
]

WSGI_APPLICATION = "wsgi.application"
ASGI_APPLICATION = "asgi.application"

# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": get_env("DB_ENGINE", "django.db.backends.postgresql"),
        "NAME": get_env("DB_NAME", "postgres"),
        "USER": get_env("DB_USER", "postgres"),
        "PASSWORD": get_env("DB_PASSWORD", "postgres"),
        "HOST": get_env("DB_HOST", "db"),
        "PORT": int(get_env("DB_PORT", "5432")),
    },
}

# Redis settings

REDIS_HOST = get_env("REDIS_HOST", "127.0.0.1")
REDIS_PORT = int(get_env("REDIS_PORT", "6379"))

# Channels

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": get_env("CHANNELS_BACKEND", "channels_redis.core.RedisChannelLayer"),
        "CONFIG": {"hosts": [(REDIS_HOST, REDIS_PORT)]},
    }
}

# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation"
        ".UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

AUTH_USER_MODEL = "profiles.User"

# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = "en-us"
TIME_ZONE = get_env("TIME_ZONE", "America/Chicago")
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

STATIC_URL = get_env("STATIC_URL", "/static/")
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static_resources"),
]
STATIC_ROOT = get_env("STATIC_ROOT", os.path.join(BASE_DIR, "public"))
MEDIA_URL = get_env("MEDIA_ROOT", "/media/")
MEDIA_ROOT = get_env("MEDIA_ROOT", os.path.join(BASE_DIR, "media"))

FILE_UPLOAD_DIRECTORY_PERMISSIONS = 0o750
FILE_UPLOAD_PERMISSIONS = 0o644


THUMBNAIL_ALIASES = {
    "profiles.Submission.file": {
        "thumbnail": {"size": (300, 300), "crop": ",0"},
        "gallery": {"size": (1000, 700)},
        "notification": {"size": (80, 80)},
    },
    "profiles.Submission.preview": {
        "thumbnail": {"size": (300, 300), "crop": False},
        "notification": {"size": (80, 80)},
    },
    "sales.Product.file": {
        "thumbnail": {"size": (300, 300), "crop": False},
        "preview": {"size": (1000, 1000), "crop": False},
        "notification": {"size": (80, 80)},
    },
    "sales.Product.preview": {
        "thumbnail": {"size": (300, 300), "crop": False},
        "notification": {"size": (80, 80)},
    },
    "sales.Revision.file": {
        "preview": {"size": (1000, 1000), "crop": False},
        "notification": {"size": (80, 80)},
    },
    "sales.Revision.preview": {
        "thumbnail": {"size": (300, 300), "crop": False},
        "notification": {"size": (80, 80)},
    },
    "sales.Reference.file": {
        "preview": {"size": (1000, 1000), "crop": False},
        "notification": {"size": (80, 80)},
    },
    "sales.Reference.preview": {
        "thumbnail": {"size": (300, 300), "crop": False},
        "notification": {"size": (80, 80)},
    },
    "": {},
}

THUMBNAIL_PRESERVE_EXTENSIONS = True

AUTHORIZE_KEY = get_env("AUTHORIZE_KEY", "")
AUTHORIZE_SECRET = get_env("AUTHORIZE_SECRET", "")

STRIPE_KEY = get_env("STRIPE_KEY", "")
STRIPE_PUBLIC_KEY = get_env("STRIPE_PUBLIC_KEY", "")

DEFAULT_CURRENCY = get_env("DEFAULT_CURRENCY", "USD")

STRIPE_CHARGE_STATIC = Money(get_env("STRIPE_CHARGE_STATIC", "0.30"), DEFAULT_CURRENCY)
STRIPE_CHARGE_PERCENTAGE = Decimal(get_env("STRIPE_CHARGE_PERCENTAGE", "2.90"))
STRIPE_INTERNATIONAL_PERCENTAGE_ADDITION = Decimal(
    get_env("STRIPE_INTERNATIONAL_PERCENTAGE_ADDITION", "1.50")
)
STRIPE_CARD_PRESENT_PERCENTAGE = Decimal(
    get_env("STRIPE_CARD_PRESENT_PERCENTAGE", "2.70")
)
STRIPE_CARD_PRESENT_STATIC = Money(
    get_env("STRIPE_CARD_PRESENT_PERCENTAGE", "0.05"), DEFAULT_CURRENCY
)
# Yes, this is .25% + $0.25. Not a copy-paste error.
STRIPE_PAYOUT_STATIC = Money(get_env("STRIPE_PAYOUT_STATIC", "0.25"), DEFAULT_CURRENCY)
STRIPE_PAYOUT_PERCENTAGE = Decimal(get_env("STRIPE_PAYOUT_PERCENTAGE", "0.25"))
STRIPE_PAYOUT_CROSS_BORDER_PERCENTAGE = Decimal(
    get_env("STRIPE_PAYOUT_CROSS_BORDER_PERCENTAGE", "0.25")
)
STRIPE_ACTIVE_ACCOUNT_MONTHLY_FEE = Money(
    get_env("STRIPE_ACTIVE_ACCOUNT_MONTHLY_FEE", "2.00"), DEFAULT_CURRENCY
)

# Stripe is now the only processor-- authorize.net has been removed. More work will be
# needed to abstract out processors to make them further pluggable, but new processors
# will more closely match Stripe (that is-- webhook driven) than Authorize.net (which
# we implemented all synchronous).
#
# Even if we re-implemented authorize.net, we should do so using its webhook structure
# instead of the synchronous method we used previously.
DEFAULT_CARD_PROCESSOR = get_env("DEFAULT_CARD_PROCESSOR", "stripe")

if TESTING:
    # Development system may have a stripe key, but we don't want to be making entries
    # on the Stripe test service
    STRIPE_KEY = ""
    STRIPE_PUBLIC_KEY = ""

DEFAULT_PROTOCOL = get_env("DEFAULT_PROTOCOL", "https")
DEFAULT_DOMAIN = get_env("DEFAULT_DOMAIN", "artconomy.vulpinity.com")
# The webhooks domain may be different in the case of local development using something
# like ngrok.
WEBHOOKS_DOMAIN = get_env("WEBHOOKS_DOMAIN", DEFAULT_DOMAIN)
PREMAILER_OPTIONS = get_env(
    "PREMAILER_OPTIONS",
    {
        "base_url": "{}://{}".format(DEFAULT_PROTOCOL, DEFAULT_DOMAIN),
        "remove_classes": False,
    },
    unpack=True,
)

VITE_DEV_MODE = bool(int(get_env("VITE_DEV_MODE", str(int(DEBUG)))))

DEFAULT_VITE_URL_PREFIX = "/vite" if VITE_DEV_MODE else "/static/dist/"

VITE_URL_PREFIX = get_env("VITE_URL_PREFIX", DEFAULT_VITE_URL_PREFIX)

DJANGO_VITE = {
    "default": {
        "dev_mode": VITE_DEV_MODE,
        "dev_server_protocol": "https",
        "dev_server_port": 443,
        "dev_server_host": DEFAULT_DOMAIN,
        "static_url_prefix": VITE_URL_PREFIX,
    }
}

# Not used by django-vite, but by our template tag defined in lib/templatetags/render_vite_bundle.py

VITE_APP_DIR = get_env("VITE_APP_DIR", STATIC_ROOT)


EMAIL_BACKEND = get_env("EMAIL_BACKEND", "djcelery_email.backends.CeleryEmailBackend")

# Settings for the SMTP backend, if using.
EMAIL_HOST = get_env("EMAIL_HOST", "localhost")
EMAIL_HOST_USER = get_env("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = get_env("EMAIL_HOST_PASSWORD", "")
EMAIL_PORT = int(get_env("EMAIL_PORT", "25"))
# These next two settings are mutually exclusive. See Django settings docs.
EMAIL_USE_SSL = bool(int(get_env("EMAIL_USE_SSL", "0")))
EMAIL_USE_TLS = bool(int(get_env("EMAIL_USE_TLS", "0")))

CELERY_EMAIL_BACKEND = get_env(
    "CELERY_EMAIL_BACKEND", "sendgrid_backend.SendgridBackend"
)
if TESTING:
    EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
DEFAULT_FROM_EMAIL = get_env(
    "DEFAULT_FROM_EMAIL", "Artconomy <notifications@artconomy.com>"
)
RETURN_PATH_EMAIL = get_env("RETURN_PATH_EMAIL", "support@artconomy.com")
SERVER_EMAIL = DEFAULT_FROM_EMAIL

CELERY_EMAIL_TASK_CONFIG = {
    "rate_limit": "50/m",
    "ignore_result": True,
}

SENDGRID_API_KEY = get_env("SENDGRID_API_KEY", "")

SANDBOX_APIS = bool(int(get_env("SANDBOX_APIS", "1")))

SENDGRID_SANDBOX_MODE_IN_DEBUG = SANDBOX_APIS
SENDGRID_ECHO_TO_STDOUT = DEBUG

MAX_CHARACTER_COUNT = int(get_env("MAX_CHARACTER_COUNT", "30"))
MAX_ATTRS = int(get_env("MAX_ATTRS", "10"))

TABLE_PERCENTAGE_FEE = Decimal(get_env("TABLE_PERCENTAGE_FEE", "10"))
TABLE_STATIC_FEE = Money(get_env("TABLE_STATIC_FEE", "5.00"), DEFAULT_CURRENCY)
TABLE_TAX = Decimal(get_env("TABLE_TAX", "8.25"))

# Add-on percentage to make sure we're always able to handle international conversions.
# 1% is always enough, as no international conversion levied by Stripe is greater than
# that.
#
# It may be possible to lower fees further if we can dynamically determine what the
# actual payout fee will be, but for the moment the effort level isn't worth it, and
# I'm not sure that there's an appropriate API endpoint for this particular
# functionality.
INTERNATIONAL_CONVERSION_PERCENTAGE = Decimal(
    get_env("INTERNATIONAL_CONVERSION_PERCENTAGE", "1")
)

# Fees for 'straight processing', like when we're handling tips. This is only very
# minimally above Stripe's fees, since we're not handling disputes. However, we might
# have to deal with a fraud issue, or a hidden stripe fee we're not calculating, so
# having some buffer for these kinds of transactions is needed.
PROCESSING_PERCENTAGE = Decimal(get_env("PROCESSING_PERCENTAGE", "3.4"))
PROCESSING_STATIC = Money(get_env("PROCESSING_PERCENTAGE", ".55"), DEFAULT_CURRENCY)
# The country that the escrow account is housed in. In all reality this will probably
# always be the US.
SOURCE_COUNTRY = get_env("SOURCE_COUNTRY", "US")

HIDE_TEST_BROWSER = bool(int(get_env("HIDE_TEST_BROWSER", "1")))

# DO NOT SET THIS TO TRUE IN PRODUCTION.
BYPASS_PAYPAL_WEBHOOK_VALIDATION = bool(
    int(get_env("BYPASS_PAYPAL_WEBHOOK_VALIDATION", "0")),
)

MIN_PASS_LENGTH = int(get_env("MIN_PASS_LENGTH", "8"))

BANNED_USERNAMES = get_env("BANNED_USERNAMES", ["artconomy"], unpack=True)
# Special username that is used by the frontend to indicate user is not logged in.
BANNED_USERNAMES += ["_"]

MINIMUM_PRICE = Money(get_env("MINIMUM_PRICE", "5.00"), DEFAULT_CURRENCY)
MINIMUM_TIP = Money(get_env("MINIMUM_TIP", "1.00"), DEFAULT_CURRENCY)
MAXIMUM_TIP = Money(get_env("MAXIMUM_TIP_AMOUNT", "100"), DEFAULT_CURRENCY)
MINIMUM_TURNAROUND = Decimal(get_env("MINIMUM_TURNAROUND", ".01"))

# Number of days after a commission is finalized where the user is prompted to tip.
TIP_DAYS = int(get_env("TIP_DAYS", "5"))

# Number of days an order will stay in Limbo before it is automatically cancelled.
LIMBO_DAYS = int(get_env("LIMBO_DAYS", "10"))

# Number of days until an order marked 'NEW' will automatically cancel and close the
# artist's commissions.
# NOTE: This will only affect new/newly commented on orders.
AUTO_CANCEL_DAYS = int(get_env("AUTO_CLOSE_DAYS", "14"))

# Grace period for paying term invoices before new orders are disabled.
TERM_GRACE_DAYS = int(get_env("TERM_GRACE_DAYS", "7"))

REFUND_FEE = Decimal(get_env("REFUND_FEE", "2.00"))

# Account ID for Drip
DRIP_ACCOUNT_ID = get_env("DRIP_ACCOUNT_ID", "")

DRIP_API_KEY = get_env("DRIP_API_KEY", "")

GA_ACCOUNT_ID = get_env("GA_ACCOUNT_ID", "")

MAILCHIMP_API_KEY = get_env("MAILCHIMP_API_KEY", "")

MAILCHIMP_LIST_SECRET = get_env("MAILCHIMP_LIST_SECRET", "")

COUNTRIES_NOT_SERVED = get_env(
    "COUNTRIES_NOT_SERVED",
    (
        "NK",
        "IR",
        "NG",
    ),
    unpack=True,
)

REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "apps.lib.middleware.ResizablePagination",
    "PAGE_SIZE": 50,
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.TokenAuthentication",
    ),
}
if not DEBUG:
    REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = (
        "rest_framework.renderers.JSONRenderer",
    )

# This could be set back to Google Recaptcha if necessary, which is
# https://www.google.com/recaptcha/api/siteverify
GR_CAPTCHA_URL = get_env("GR_CAPTCHA_URL", "https://hcaptcha.com/siteverify")

GR_CAPTCHA_SECRET_KEY = get_env("GR_CAPTCHA_SECRET_KEY", "")

GR_CAPTCHA_PUBLIC_KEY = get_env("GR_CAPTCHA_PUBLIC_KEY", "")


LOGGING = None

# Uncomment when tests need debugging.
# Make sure to comment out the logging disable line in the next section as well.

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

if TESTING:
    PASSWORD_HASHERS = [
        "django.contrib.auth.hashers.MD5PasswordHasher",
    ]
    # Uncomment this when doing heavy test debugging.
    logging.disable(logging.CRITICAL)


if ("test" not in argv) and ("runserver" not in argv):
    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "console": {
                # exact format is not important, this is the minimum information
                "format": "%(asctime)s %(name)-12s %(levelname)-8s %(message)s",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "console",
            },
            "mail_admins": {
                "level": "ERROR",
                "class": "django.utils.log.AdminEmailHandler",
            },
        },
        "loggers": {
            # root logger
            "": {
                "level": "ERROR",
                "handlers": ["console"],
            },
        },
    }

AVATAR_EXPOSE_USERNAMES = False

AVATAR_THUMB_FORMAT = "PNG"

# Django-avatar chokes when deleting files in a test environment
if TESTING:
    AVATAR_CLEANUP_DELETED = False

# Default: one year.
SESSION_COOKIE_AGE = int(get_env("SESSION_COOKIE_AGE", str(60 * 60 * 24 * 365)))

TELEGRAM_BOT_KEY = get_env("TELEGRAM_BOT_KEY", "")
TELEGRAM_BOT_USERNAME = get_env("TELEGRAM_BOT_USERNAME", "")

RABBIT_HOST = get_env("RABBIT_HOST", "rabbit")
RABBIT_PORT = int(get_env("RABBIT_PORT", "5672"))

CELERY_ALWAYS_EAGER = bool(int(get_env("CELERY_ALWAYS_EAGER", "0")))

CELERY_BROKER_CONNECTION_RETRY = bool(
    int(get_env("CELERY_BROKER_CONNECTION_RETRY", True))
)

CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = bool(
    int(get_env("CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP", True))
)

CELERYBEAT_SCHEDULE = {
    "run_billing": {
        "task": "apps.sales.tasks.run_billing",
        "schedule": crontab(minute=0, hour=0),
    },
    "auto_finalize_run": {
        "task": "apps.sales.tasks.auto_finalize_run",
        "schedule": crontab(hour=1, minute=0),
    },
    "remind_sales": {
        "task": "apps.sales.tasks.remind_sales",
        "schedule": crontab(hour=15, minute=30),
    },
    "destroy_cancelled": {
        "task": "apps.sales.tasks.clear_cancelled_deliverables",
        "schedule": crontab(hour=3, minute=10),
    },
    "annotate_payouts": {
        "task": "apps.sales.tasks.annotate_connect_fees",
        "schedule": crontab(hour=1, minute=30),
    },
    "destroy_abandoned_tips": {
        "task": "apps.sales.tasks.destroy_abandoned_tips",
        "schedule": crontab(hour=1, minute=45),
    },
    "clear_hitcount_tables": {
        "task": "apps.lib.tasks.clear_hitcount_tables",
        "schedule": crontab(hour=2, minute=30),
    },
    "cancel_abandoned_orders": {
        "task": "apps.sales.tasks.cancel_abandoned_orders",
        "schedule": crontab(hour=2, minute=45),
    },
}

ENV_NAME = get_env("ENV_NAME", "prod")

OTP_TOTP_ISSUER = get_env("OTP_TOTP_ISSUER", "Artconomy")

TEST_RUNNER = "apps.lib.test_resources.NPMBuildTestRunner"


AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation"
        ".UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {
            "min_length": 8,
        },
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"redis://{REDIS_HOST}:{REDIS_PORT}/1",
    },
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

DEFAULT_SERVICE_PLAN_NAME = get_env("DEFAULT_SERVICE_PLAN_NAME", "Free")
# Used as the comparison point in price previews by the frontend.
PREFERRED_SERVICE_PLAN_NAME = get_env("PREFERRED_SERVICE_PLAN_NAME", "Landscape")

# Username for the 'anonymous user'-- The user which random purchases at the point of
# sale are attributed to.
# This exists so the software can distinguish between None as a payer/payee, which means
# Artconomy, and someone who doesn't have an account without having to create a guest
# user each time.
#
# The create_anonymous_user command must be run to create this user.
ANONYMOUS_USER_USERNAME = get_env("ANONYMOUS_USER_USERNAME", "Anonymous")

ANONYMOUS_USER_EMAIL = get_env("ANONYMOUS_USER_EMAIL", "anonymous@artconomy.com")

HITCOUNT_KEEP_HIT_IN_DATABASE = {
    "days": int(get_env("HITCOUNT_KEEP_HIT_IN_DATABASE", "30"))
}

MASTODON_PROFILES = get_env(
    "MASTODON_PROFILES",
    [
        "https://yiff.life/@Vulpes_Veritas",
        "https://mastodon.social/@Artconomy",
    ],
    unpack=True,
)

# Discord bot settings
DISCORD_BOT_KEY = get_env("DISCORD_BOT_KEY", "fake-bot-key")
DISCORD_CLIENT_KEY = get_env("DISCORD_CLIENT_KEY", "discord-client-key")
DISCORD_CLIENT_SECRET = get_env("DISCORD_CLIENT_SECRET", "discord-client-secret")
# Explicitly set to empty string if not filled out in .env file by docker-compose
DISCORD_GUILD_ID = int(get_env("DISCORD_GUILD_ID", "12345678") or "0")


COMMUNITY_ACCOUNT_NAMES = get_env(
    "COMMUNITY_ACCOUNT_NAMES", ["DoodleSessions"], unpack=True
)

USER_AGENT = get_env("USER_AGENT", "Artconomy (fox@artconomy.com)")

DEDUPLICATE_ASSETS = get_env("DEDUPLICATE_ASSETS", not DEBUG)


# CSP Content settings

# Stripe required settings reference: https://docs.stripe.com/connect/get-started-connect-embedded-components#csp-and-http-header-requirements
CSP_IMG_SRC = tuple(
    get_env(
        "CSP_IMG_SRC",
        (
            "'self'",
            "https://*.stripe.com",
            "https://www.gravatar.com/",
            # Blog post images on the front page won't load without this.
            "https://artconomy.com/",
        ),
        unpack=True,
    )
)

CSP_STYLE_SRC = tuple(
    get_env(
        "CSP_STYLE_SRC",
        (
            "'self'",
            "'unsafe-inline'",
        ),
        unpack=True,
    )
)

CSP_SCRIPT_SRC = tuple(
    get_env(
        "CSP_SCRIPT_SRC",
        (
            "'self'",
            "'unsafe-inline'",
            "data:",
            "blob:",
            "https://sentry.io",
            "https://www.googletagmanager.com",
            "https://static.cloudflareinsights.com",
            "https://artconomy.matomo.cloud",
            "https://cdn.matomo.cloud",
            "https://hcaptcha.com",
            "https://*.stripe.com/",
            "https://*.hcaptcha.com",
        ),
        unpack=True,
    )
)

CSP_CONNECT_SRC = tuple(
    get_env(
        "CSP_CONNECT_SRC",
        (
            "'self'",
            "https://*.cloudflareinsights.com",
            "https://sentry.io",
            "https://artconomy.matomo.cloud",
        ),
        True,
    )
)

CSP_FRAME_SRC = tuple(
    get_env(
        "CSP_FRAME_SRC",
        (
            "'self'",
            "https://connect-js.stripe.com",
            "https://js.stripe.com",
            "https://hcaptcha.com",
            "https://*.hcaptcha.com",
            "https://www.youtube-nocookie.com",
        ),
    )
)

# Sites

SITE_ID = int(get_env("SITE_ID", "1"))

# Used in the initial sites migration.

SITE_DOMAIN_NAME = get_env("SITE_DOMAIN_NAME", DEFAULT_DOMAIN)

SITE_DISPLAY_NAME = get_env(
    "SITE_DISPLAY_NAME", SITE_DOMAIN_NAME.replace("www.", "", 1).capitalize()
)

# Sitemaps

# Included external sitemaps. This is for doing things like making sure our WordPress
# blog's generated sitemap data is included in the global listings.

EXTERNAL_SITEMAPS = get_env(
    "EXTERNAL_SITEMAPS",
    {
        "BlogPosts": "https://artconomy.com/blog/post-sitemap.xml",
        "BlogCategories": "https://artconomy.com/blog/category-sitemap.xml",
        "BlogTags": "https://artconomy.com/blog/post_tag-sitemap.xml",
    },
    unpack=True,
)

# These settings used by django-static-sitemaps
STATICSITEMAPS_ROOT_SITEMAP = "conf.sitemaps.sitemaps"

STATICSITEMAPS_MOCK_SITE_NAME = DEFAULT_DOMAIN

STATICSITEMAPS_ROOT_DIR = str(Path(STATIC_ROOT) / "sitemaps")

STATICSITEMAPS_URL = str(Path(STATIC_URL) / "sitemaps")
