from collections import OrderedDict

from django.apps import apps
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.mail import EmailMessage
from django.db.models.query import ModelIterable

from django.http import Http404
from django.template.loader import get_template
from django.views import View
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import (
    RetrieveUpdateDestroyAPIView, get_object_or_404,
    GenericAPIView, ListCreateAPIView,
    ListAPIView)
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from reversion.models import VersionQuerySet, Version

from apps.lib.middleware import OlderThanPagination
from apps.lib.models import Comment, Asset
from apps.lib.permissions import (
    CommentEditPermission, CommentViewPermission, CommentDepthPermission, Any, All,
    IsMethod, IsSafeMethod, CanComment,
    CanListComments,
    IsAuthenticatedObj, IsStaff)
from apps.lib.serializers import CommentSerializer, CommentSubscriptionSerializer
from apps.lib.utils import (
    countries_tweaked, remove_comment, safe_add, default_context,
    get_client_ip
)
from apps.profiles.models import User
from apps.profiles.permissions import ObjectControls, IsRegistered
from apps.profiles.serializers import ContactSerializer
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

    def fake_destroy(self, instance):
        instance.text = ''
        instance.deleted = True
        if instance.comments.all().filter(deleted=True).count() == instance.comments.all().count():
            instance.thread_deleted = True
        instance.save()

    def real_destroy(self, instance):
        target = instance.content_object
        if not instance.comments.all().exists() or not target:
            instance.delete()
            if target and isinstance(target, Comment):
                if target.deleted and not target.comments.all().exists():
                    target.delete()
        else:
            instance.text = ''
            instance.deleted = True
            instance.save()

    def perform_destroy(self, instance):
        remove_comment(instance.id)
        if getattr(instance.top, 'preserve_comments', False):
            self.fake_destroy(instance)
        else:
            self.real_destroy(instance)
        if hasattr(instance.top, 'comment_deleted'):
            instance.top.comment_deleted(instance)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.check_object_permissions(request, instance)
        self.perform_destroy(instance)
        if instance.deleted:
            # Soft deleted.
            return Response(
                status=status.HTTP_200_OK,
                data=CommentSerializer(instance=instance, context=self.get_serializer_context()).data,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_serializer(self, instance, *args, **kwargs):
        kwargs['context'] = self.get_serializer_context()
        if self.request.user.is_staff:
            return CommentSerializer(instance=instance, *args, **kwargs)
        if self.request.user == instance.user:
            return CommentSerializer(instance=instance, *args, **kwargs)
        return CommentSubscriptionSerializer(instance=instance, *args, **kwargs)


class Comments(ListCreateAPIView):
    permission_classes = [
        Any(
            All(IsSafeMethod, CanListComments),
            All(IsMethod('POST'), IsAuthenticated, CanComment, CommentDepthPermission),
        ),
    ]
    serializer_class = CommentSerializer
    pagination_class = OlderThanPagination

    # noinspection PyAttributeOutsideInit
    def get_object(self):
        invalid_model = ValidationError({
            'content_type': [
                f"Could not find content type {self.kwargs['content_type']}. "
                f'Make sure it is a valid, commentable model and is in app.Model format.',
            ],
        })
        try:
            model_spec = (self.kwargs['content_type'] + '.').split('.')[:2]
            model = apps.get_model(*model_spec)
            # Avoid leaking data about what models are installed.
            permissions_set = getattr(model, 'comment_view_permissions', getattr(model, 'comment_permissions', None))
            if permissions_set is None:
                raise invalid_model
        except (LookupError, IndexError):
            raise invalid_model
        self.target = get_object_or_404(model, id=self.kwargs['object_id'])
        return self.target

    def get_queryset(self):
        qs = self.target.comments.all()
        if not (self.request.user.is_staff and self.request.GET.get('history', False)):
            qs = qs.filter(thread_deleted=False)
        return qs.select_related('user').order_by('-created_on')

    def post(self, *args, **kwargs):
        target = self.get_object()
        self.check_object_permissions(self.request, target)
        return super(Comments, self).post(*args, **kwargs)

    def get(self, *args, **kwargs):
        target = self.get_object()
        self.check_object_permissions(self.request, target)
        return super(Comments, self).get(*args, **kwargs)

    def perform_create(self, serializer):
        if isinstance(self.target, Comment):
            top = self.target.top
        else:
            top = self.target
        comment = serializer.save(
            user=self.request.user,
            content_type=ContentType.objects.get_for_model(self.target),
            object_id=self.target.id,
            top_object_id=top.id,
            top_content_type=ContentType.objects.get_for_model(top)
        )
        return comment


def annotate_revision(version):
    obj = version._object_version.object
    obj.id = version.id
    return obj


class ModelVersionIterable(ModelIterable):
    def __iter__(self):
        yield from (
            annotate_revision(version)
            for version in ModelIterable.__iter__(self)
        )


class VersionHistoryQuerySet(VersionQuerySet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._iterable_class = ModelVersionIterable


class CommentHistory(ListAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsStaff]

    def get_object(self):
        comment = get_object_or_404(
            Comment, id=self.kwargs['comment_id']
        )
        self.check_object_permissions(self.request, comment)
        return comment

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['history'] = True
        return context

    def get_queryset(self):
        for comment in VersionHistoryQuerySet(Version).get_for_object(self.get_object()).all():
            print(comment)
        return VersionHistoryQuerySet(Version).get_for_object(self.get_object()).all()


class CountryListing(APIView):
    # noinspection PyMethodMayBeStatic
    def get(self, _request):
        return Response(status=status.HTTP_200_OK, data=OrderedDict(countries_tweaked()))


class BaseUserTagView(GenericAPIView):
    field_name = 'shared_with'
    permission_classes = [IsRegistered, ObjectControls]

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

    # noinspection PyUnusedLocal
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

    # noinspection PyUnusedLocal
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

    # noinspection PyMethodMayBeStatic
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


class SupportRequest(APIView):
    # noinspection PyMethodMayBeStatic
    def post(self, request):
        serializer = ContactSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        subject = 'New Support Request'
        from_email = serializer.validated_data['email']
        username = '<Anonymous>'
        if request.user.is_authenticated:
            username = request.user.username
        ctx = {
            'body': serializer.validated_data['body'],
            'ip': get_client_ip(request),
            'username': username,
            'path': serializer.validated_data['referring_url'],
            'user_agent': request.META.get('HTTP_USER_AGENT')
        }
        message = get_template('support_email.txt').render(ctx)
        msg = EmailMessage(
            subject,
            message,
            to=[settings.ADMINS[0][1]],
            headers={'Reply-To': from_email}
        )
        msg.send()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AssetUpload(APIView):
    permission_classes = [IsRegistered]
    parser_classes = (MultiPartParser,)

    # noinspection PyMethodMayBeStatic
    def post(self, request):
        file_obj = request.data.get('files[]')
        if not file_obj:
            raise ValidationError({'files[]': ['This field is required.']})
        asset = Asset(file=file_obj, uploaded_by=request.user)
        asset.clean()
        asset.save()
        return Response(data={'id': str(asset.id)})
