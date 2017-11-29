from django.conf.urls import url

from apps.lib.views import CommentUpdate, CommentReply

urlpatterns = [
    url(
        r'^v1/comment/(?P<comment_id>\d+)/$', CommentUpdate.as_view(),
        name='comment'
    ),
    url(
        r'^v1/comment/(?P<comment_id>\d+)/reply/$', CommentReply.as_view(),
        name='comment'
    )
]
