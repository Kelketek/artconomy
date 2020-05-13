"""artconomy URL Configuration
"""
from django.urls import path

from apps.profiles import views

app_name = "profiles"

# These URLs/views are for the purpose of getting Meta tag preview information.


urlpatterns = [
    path('<username>/characters/<character>', views.CharacterPreview.as_view(), name='character_preview'),
    path('<username>/gallery/art', views.ArtPreview.as_view(), name='art_preview'),
    path('<username>/gallery/collection', views.CollectionPreview.as_view(), name='art_preview'),
]
