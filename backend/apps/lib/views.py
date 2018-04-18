from collections import OrderedDict

from rest_framework import status
from rest_framework.generics import RetrieveUpdateDestroyAPIView, get_object_or_404, CreateAPIView, UpdateAPIView, \
    GenericAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.lib.models import Comment
from apps.lib.permissions import CommentEditPermission, CommentViewPermission, CommentDepthPermission, Any, All, \
    IsMethod, IsSafeMethod
from apps.lib.serializers import CommentSerializer, CommentSubscriptionSerializer
from apps.lib.utils import countries_tweaked, remove_tags, add_tags, remove_comment


class CommentUpdate(RetrieveUpdateDestroyAPIView):
    serializer_class = CommentSerializer
    permission_classes = [
        Any(
            CommentEditPermission,
            All(IsMethod('PUT'), CommentViewPermission),
            All(IsSafeMethod, CommentViewPermission)
        )
    ]

    def get_object(self):
        comment = get_object_or_404(
            Comment, id=self.kwargs['comment_id']
        )
        self.check_object_permissions(self.request, comment)
        return comment

    def perform_destroy(self, instance):
        remove_comment(instance.id)
        if not instance.children.all():
            instance.delete()
        else:
            instance.text = ''
            instance.deleted = True
            instance.save()

    def put(self, request, *args, **kwargs):
        instance = self.get_object()
        data = {'subscribed': request.data.get('subscribed')}
        serializer = CommentSubscriptionSerializer(instance=instance, data=data, context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_200_OK, data=serializer.data)


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


class BaseTagView(GenericAPIView):
    field_name = 'tags'

    def get_object(self):
        """
        Override this method with whatever is needed to get the target for tagging.
        """
        raise NotImplementedError

    def post_delete(self, target, result):
        """
        Override this method with whatever is needed after deleting tags.
        """
        raise NotImplementedError

    def delete(self, request, *args, **kwargs):
        target = self.get_object()
        self.check_object_permissions(request, target)
        success, result = remove_tags(request, target, field_name=self.field_name)
        if not success:
            return result

        return self.post_delete(target, result)

    def post_post(self, target, result):
        raise NotImplementedError

    def post(self, request, *args, **kwargs):
        target = self.get_object()
        self.check_object_permissions(request, target)
        success, result = add_tags(request, target, field_name=self.field_name)
        if not success:
            return result

        return self.post_post(target, result)
