from apps.lib import consumers
from django.urls import re_path

websocket_urlpatterns = [
    re_path(r"ws/events/$", consumers.EventConsumer.as_asgi()),
]
