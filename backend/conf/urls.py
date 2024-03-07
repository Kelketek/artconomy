"""backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""

import re
import sys

import views
from django.conf import settings
from django.contrib import admin
from django.core.exceptions import ImproperlyConfigured
from django.urls import include, re_path
from django.views.static import serve
from django_otp.admin import OTPAdminSite

if not settings.DEBUG:
    admin.site.__class__ = OTPAdminSite

urlpatterns = [
    re_path(r"^admin/", admin.site.urls),
    re_path(r"^api-auth/", include("rest_framework.urls", namespace="rest_framework")),
    re_path(r"^profile/", include("apps.profiles.profile_urls", namespace="profile")),
    re_path(
        r"^submissions/",
        include("apps.profiles.submission_urls", namespace="submissions"),
    ),
    re_path(r"^store/", include("apps.sales.store_urls", namespace="store")),
    re_path(r"^api/profiles/", include("apps.profiles.urls", namespace="profiles")),
    re_path(r"^api/sales/", include("apps.sales.urls", namespace="sales")),
    re_path(r"^api/lib/", include("apps.lib.urls", namespace="lib")),
    re_path(r"^api/tg_bot/", include("apps.tg_bot.urls", namespace="tg_bot")),
    re_path(r"^api/", views.bad_endpoint, name="api404"),
    re_path(r"^force-error-email/", views.force_error_email, name="force_error"),
    re_path(r"^test-telegram/", views.test_telegram, name="test_telegram"),
    re_path(r"^discord/", include("apps.discord_bot.urls", namespace="discord_bot")),
]


def static(prefix, view=serve, **kwargs):
    """
    Version of the static views that DOESN'T check for the DEBUG flag since we're
    checking it elsewhere and static items are needed for e2e tests.

    NOTICE: Sometimes the Staticfiles app decides to do whatever it wants and then
    reports this view was the one that did it. If you can't print from the serve
    function, it's full of shit. Check the STATICFILES_DIRS instead.
    """
    if not prefix:
        raise ImproperlyConfigured("Empty static prefix not permitted")
    elif "://" in prefix:
        # No-op if not in debug mode or a non-local prefix.
        return []
    return [
        re_path(
            r"^%s(?P<path>.*)$" % re.escape(prefix.lstrip("/")), view, kwargs=kwargs
        ),
    ]


if settings.DEBUG or "test" in sys.argv:
    urlpatterns += static("/js/", document_root=settings.STATIC_ROOT + "/dist/js/")
    urlpatterns += static("/css/", document_root=settings.STATIC_ROOT + "/dist/css/")
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += [re_path(r"^", views.index)]

handler400 = views.error
handler403 = views.error
handler404 = views.error
handler500 = views.index
