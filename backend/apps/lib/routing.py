from django.urls import re_path
from apps.lib import consumers

websocket_urlpatterns = [
    re_path(r'ws/events/$', consumers.EventConsumer.as_asgi()),
]
