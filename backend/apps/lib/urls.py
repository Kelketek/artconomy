from django.urls import path

from apps.lib import views

app_name = 'lib'

urlpatterns = [
    path('v1/read-marker/<content_type>/<object_id>/', views.MarkRead.as_view()),
    path('v1/comments/<content_type>/<object_id>/', views.Comments.as_view()),
    # Convenience alias so that comment singles can chain URLs on the front-end.
    path(
        'v1/comments/<content_type>/<object_id>/<int:comment_id>/', views.CommentUpdate.as_view(),
        name='comment'
    ),
    path(
        'v1/comments/lib.Comment/<int:comment_id>/history/', views.CommentHistory.as_view(),
        name='comment_history'
    ),
    path(
        'v1/countries/', views.CountryListing.as_view(), name='country_listing'
    ),
    path('v1/support/request/', views.SupportRequest.as_view(), name='support_request'),
    path('v1/asset/', views.AssetUpload.as_view(), name='asset_upload'),
    path('v1/noop/', views.NoOp.as_view(), name='no_op'),
]
