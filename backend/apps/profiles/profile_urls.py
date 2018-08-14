"""artconomy URL Configuration
"""
from django.urls import path

from apps.profiles.views import CharacterPreview

app_name = "profiles"

# These URLs/views are for the purpose of getting Meta tag preview information.


urlpatterns = [
    path('<username>/characters/<character>', CharacterPreview.as_view(), name='character_preview'),
]
