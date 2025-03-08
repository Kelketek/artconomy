"""artconomy URL Configuration"""

from apps.profiles import views
from apps.sales.views import main as sales_views
from django.urls import path

app_name = "profiles"

# These URLs/views are for the purpose of getting Meta tag preview information.


urlpatterns = [
    path(
        "<username>/characters/<character>",
        views.CharacterPreview.as_view(),
        name="character_preview",
    ),
    path(
        "<username>/characters/<character>/",
        views.CharacterPreview.as_view(),
        name="character_preview",
    ),
    path("<username>/gallery/art", views.ArtPreview.as_view(), name="art_preview"),
    path("<username>/gallery/art/", views.ArtPreview.as_view(), name="art_preview"),
    path(
        "<username>/gallery/collection",
        views.CollectionPreview.as_view(),
        name="art_preview",
    ),
    path(
        "<username>/gallery/collection/",
        views.CollectionPreview.as_view(),
        name="art_preview",
    ),
    path("<username>/products", sales_views.StorePreview.as_view(), name="art_preview"),
    path(
        "<username>/products/", sales_views.StorePreview.as_view(), name="art_preview"
    ),
    path("<username>/about", views.ProfilePreview.as_view(), name="profile_preview"),
    path("<username>/about/", views.ProfilePreview.as_view(), name="profile_preview"),
    path("<username>", views.ProfilePreview.as_view(), name="root_profile_preview"),
    path("<username>/", views.ProfilePreview.as_view(), name="root_profile_preview"),
]
