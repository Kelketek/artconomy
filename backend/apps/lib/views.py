from collections import OrderedDict

from django.http import Http404
from django.views import View
from rest_framework import status
from rest_framework.generics import RetrieveUpdateDestroyAPIView, get_object_or_404, CreateAPIView, \
    GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.lib.models import Comment
from apps.lib.permissions import CommentEditPermission, CommentViewPermission, CommentDepthPermission, Any, All, \
    IsMethod, IsSafeMethod, IsAuthenticatedObj
from apps.lib.serializers import CommentSerializer, CommentSubscriptionSerializer
from apps.lib.utils import countries_tweaked, remove_tags, add_tags, remove_comment, safe_add, default_context
from apps.profiles.models import User
from apps.profiles.permissions import ObjectControls
from views import bad_request, base_template


class CommentUpdate(RetrieveUpdateDestroyAPIView):
    serializer_class = CommentSerializer
    permission_classes = [
        Any(
            CommentEditPermission,
            All(IsMethod('PUT'), CommentViewPermission, IsAuthenticatedObj),
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
        serializer = CommentSubscriptionSerializer(
            instance=instance, data=data, context=self.get_serializer_context(), partial=True
        )
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


class BaseUserTagView(GenericAPIView):
    field_name = 'shared_with'
    permission_classes = [IsAuthenticated, ObjectControls]

    def get_target(self):
        raise NotImplementedError()

    def get_serializer_context(self):
        return {'request': self.request}

    def notify(self, user, target):
        raise NotImplementedError()

    def recall(self, target, qs):
        raise NotImplementedError()

    def free_delete_check(self, target):
        raise NotImplementedError()

    def delete(self, request, *args, **kwargs):
        target = self.get_target()
        self.check_object_permissions(request, target)
        # Check has to be different here.
        # Might find a way to better simplify this sort of permission checking if
        # we end up doing it a lot.
        if self.field_name not in request.data:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={self.field_name: ['This field is required.']})
        try:
            id_list = request.data.getlist(self.field_name)
        except AttributeError:
            id_list = request.data.get(self.field_name)
        qs = User.objects.filter(id__in=id_list)
        if self.free_delete_check(target):
            getattr(target, self.field_name).remove(*qs)
            self.recall(target, qs)
            return Response(
                status=status.HTTP_200_OK,
                data=self.serializer_class(
                    instance=target, context=self.get_serializer_context()
                ).data
            )
        else:
            qs = qs.filter(id=request.user.id)
        if not qs.exists():
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={'artists': [
                    'No users specified. Those IDs do not exist, or you do not have permission '
                    'to remove any of them.'
                ]}
            )
        getattr(target, self.field_name).remove(*qs)
        return Response(
            status=status.HTTP_200_OK, data=self.serializer_class(
                instance=target, context=self.get_serializer_context()
            ).data
        )

    def post(self, request, *args, **kwargs):
        target = self.get_target()
        self.check_object_permissions(request, target)
        if self.field_name not in request.data:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={self.field_name: ['This field is required.']})
        try:
            id_list = request.data.getlist(self.field_name)
        except AttributeError:
            id_list = request.data.get(self.field_name)
        qs = User.objects.filter(id__in=id_list)
        qs = qs.exclude(id__in=getattr(target, self.field_name).all().values_list('id', flat=True))

        for user in qs:
            self.notify(user, target)
        safe_add(target, self.field_name, *qs)
        return Response(
            status=status.HTTP_200_OK, data=self.serializer_class(
                instance=target, context=self.get_serializer_context()
            ).data
        )


class BasePreview(View):
    post = staticmethod(bad_request)
    patch = staticmethod(bad_request)
    delete = staticmethod(bad_request)
    put = staticmethod(bad_request)
    head = staticmethod(bad_request)
    options = staticmethod(bad_request)
    permission_classes = []
    args = []
    kwargs = {}
    request = None

    def default_context(self):
        return default_context()

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        return [permission() for permission in self.permission_classes]

    def check_permissions(self, request):
        """
        Check if the request should be permitted.
        Raises an appropriate exception if the request is not permitted.
        """
        for permission in self.get_permissions():
            if not permission.has_permission(request, self):
                return False
        return True

    def check_object_permissions(self, request, obj):
        """
        Check if the request should be permitted for a given object.
        Raises an appropriate exception if the request is not permitted.
        """
        for permission in self.get_permissions():
            if not permission.has_object_permission(request, self, obj):
                return False
        return True

    def context(self, *args, **kwargs):
        return {}

    def get(self, request, *args, **kwargs):
        self.request = request
        self.args = args
        self.kwargs = kwargs
        try:
            context = self.context(*args, **kwargs)
        except Http404:
            context = self.default_context()
        return base_template(request, context)
