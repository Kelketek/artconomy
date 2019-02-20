from django.urls import path

from apps.lib.views import CommentUpdate, CommentReply, CountryListing, SupportRequest

app_name = 'lib'

urlpatterns = [
    path(
        'v1/comment/<int:comment_id>/', CommentUpdate.as_view(),
        name='comment'
    ),
    path(
        'v1/comment/<int:comment_id>/reply/', CommentReply.as_view(),
        name='comment'
    ),
    path(
        'v1/countries/', CountryListing.as_view(), name='country_listing'
    ),
    path('v1/support/request/', SupportRequest.as_view(), name='support_request'),
]
