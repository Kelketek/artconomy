"""
WSGI config for artconomy project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/howto/deployment/wsgi/
"""

import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

from apps.lib.routing import websocket_urlpatterns

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "conf.settings")

application = ProtocolTypeRouter({
    'http': get_asgi_application(),  # pylint: disable=invalid-name,
    'websocket': AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns,
        )
    )
})
