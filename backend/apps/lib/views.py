from collections import OrderedDict

from rest_framework import status
from rest_framework.generics import RetrieveUpdateDestroyAPIView, get_object_or_404, CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.lib.models import Comment
from apps.lib.permissions import CommentEditPermission, CommentViewPermission, CommentDepthPermission
from apps.lib.serializers import CommentSerializer
from apps.lib.utils import countries_tweaked


class CommentUpdate(RetrieveUpdateDestroyAPIView):
    serializer_class = CommentSerializer
    permission_classes = [CommentEditPermission]

    def get_object(self):
        comment = get_object_or_404(
            Comment, id=self.kwargs['comment_id']
        )
        self.check_object_permissions(self.request, comment)
        return comment

    def perform_destroy(self, instance):
        if not instance.children.all():
            instance.delete()
        else:
            instance.text = ''
            instance.deleted = True
            instance.save()


class CommentReply(CreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [CommentViewPermission, CommentDepthPermission]

    def get_object(self):
        return get_object_or_404(
            Comment, id=self.kwargs['comment_id']
        )

    def perform_create(self, serializer):
        parent = self.get_object()
        self.check_object_permissions(self.request, parent)
        return serializer.save(parent=parent, user=self.request.user)


class CountryListing(APIView):
    def get(self, _request):
        return Response(status=status.HTTP_200_OK, data=OrderedDict(countries_tweaked()))
