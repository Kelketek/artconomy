from apps.lib import views
from django.urls import path

app_name = "lib"

urlpatterns = [
    path("read-marker/<content_type>/<object_id>/", views.MarkRead.as_view()),
    path("comments/<content_type>/<object_id>/", views.Comments.as_view()),
    # Convenience alias so that comment singles can chain URLs on the front-end.
    path(
        "comments/<content_type>/<object_id>/<int:comment_id>/",
        views.CommentUpdate.as_view(),
        name="comment",
    ),
    path(
        "comments/lib.Comment/<int:comment_id>/history/",
        views.CommentHistory.as_view(),
        name="comment_history",
    ),
    path("countries/", views.CountryListing.as_view(), name="country_listing"),
    path("support/request/", views.SupportRequest.as_view(), name="support_request"),
    path("asset/<uuid:pk>/", views.AssetDetail.as_view(), name="asset_detail"),
    path("asset/", views.AssetUpload.as_view(), name="asset_upload"),
    path("noop/", views.NoOp.as_view(), name="no_op"),
]
