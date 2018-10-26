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
from django.conf import settings
from django.conf.urls import url, include
from django.contrib import admin
from django.core.exceptions import ImproperlyConfigured
from django.urls import path
from django.views.generic import RedirectView
from django.views.static import serve

import views


urlpatterns = [
    # Don't allow login through the admin's login system. It doesn't respect our 2FA implementation.
    path('admin/login/', RedirectView.as_view(url='/auth/login/')),
    url(r'^admin/', admin.site.urls),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^profile/', include('apps.profiles.profile_urls', namespace='profile')),
    url(r'^submissions/', include('apps.profiles.submission_urls', namespace='submissions')),
    url(r'^store/', include('apps.sales.store_urls', namespace='store')),
    url(r'^api/profiles/', include('apps.profiles.urls', namespace='profiles')),
    url(r'^api/sales/', include('apps.sales.urls', namespace='sales')),
    url(r'^api/lib/', include('apps.lib.urls', namespace='lib')),
    url(r'^api/tg_bot/', include('apps.tg_bot.urls', namespace='tg_bot')),
    url(r'^api/', views.bad_endpoint, name='api404'),
    url(r'^force-error-email/', views.force_error_email, name='force_error'),
    url(r'^test-telegram/', views.test_telegram, name='test_telegram')
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
    elif '://' in prefix:
        # No-op if not in debug mode or a non-local prefix.
        return []
    return [
        url(r'^%s(?P<path>.*)$' % re.escape(prefix.lstrip('/')), view, kwargs=kwargs),
    ]


if settings.DEBUG or 'test' in sys.argv:
    urlpatterns += static('/js/', document_root=settings.STATIC_ROOT + '/dist/js/')
    urlpatterns += static('/css/', document_root=settings.STATIC_ROOT + '/dist/css/')
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += [url(r'^', views.index)]
