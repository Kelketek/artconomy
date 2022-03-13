from logging import getLogger
from typing import List, Type

from django.views import View
from rest_framework.permissions import BasePermission, SAFE_METHODS, IsAuthenticated
from rest_framework.request import Request

logger = getLogger(__name__)


class CommentEditPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj.deleted:
            return False
        if obj.user == request.user:
            return True
        if request.user.is_staff:
            return True


class CommentViewPermission(BasePermission):
    """
    Checks if a user has permission to view/comment on a particular comment object.
    """
    message = "You do not have permission to comment on this."

    def has_object_permission(self, request, view, obj):
        # Jump to the top of the thread.
        while obj.parent:
            obj = obj.parent
        if obj.content_object is None:
            # Can't comment on something which doesn't exist. Also, log this.
            logger.debug("Attempted to comment on non-existent object. Comment ID was %s", obj.id)
            return False
        if obj.system:
            return False
        if request.user.is_staff:
            return True
        permission_check = getattr(
            obj.content_object, 'comment_view_permissions', getattr(obj.content_object, 'comment_permissions', None)
        )
        if permission_check is None:
            return False
        target = obj.content_object
        if not all((perm().has_object_permission(request, view, target) for perm in permission_check)):
            return False
        return True


class CommentDepthPermission(BasePermission):
    message = 'Comments are limited to top-level threads.'

    def has_object_permission(self, request, view, obj):
        from apps.lib.models import Comment
        if not hasattr(obj, 'content_object'):
            # Target isn't a comment, so this is top level.
            return True
        # Limit comment depth for now.
        if obj.content_object and isinstance(obj.content_object, Comment):
            return False
        return True


# Use CamelCase since it outputs custom class.
def ObjectStatus(statuses, message):
    class PermClass(BasePermission):
        def has_object_permission(self, request, view, obj):
            if obj.status in self.statuses:
                return True
            return False

    # Scoping doesn't work when assigning in the definition.
    PermClass.statuses = statuses
    PermClass.message = message

    return PermClass


class IsStaff(BasePermission):
    message = 'You do not have sufficient privileges to perform this operation.'

    def has_permission(self, request: Request, view: View) -> bool:
        return request.user.is_staff


class IsAnonymous(BasePermission):
    def has_permission(self, request, view):
        return not request.user.is_authenticated


class IsSafeMethod(BasePermission):
    """
    Is a read-only request.
    """
    message = 'You are not permitted to perform mutating operations on this endpoint.'

    def has_permission(self, request, view):
        return request.method in SAFE_METHODS

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class IsAuthenticatedObj(IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        return request.user and request.user.is_authenticated


def IsMethod(*method_list: str):
    class MethodCheck(BasePermission):
        def has_permission(self, request, view):
            return request.method in method_list

        def has_object_permission(self, request, view, obj):
            return self.has_permission(request, view)
    return MethodCheck


class ComboPermission(BasePermission):
    message = ''

    def run_check(self, perm, func_name, *args):
        result = getattr(perm, func_name)(*args)
        if not result and not self.message:
            self.message = getattr(perm, 'message', self.message)
        return result


def Any(*perms: Type[BasePermission]) -> Type[ComboPermission]:
    perms = [perm() for perm in perms]

    class AnyPerm(ComboPermission):
        def has_permission(self, request, view):
            return any(self.run_check(perm, 'has_permission', request, view) for perm in perms)

        def has_object_permission(self, request, view, obj):
            result = any(self.run_check(perm, 'has_object_permission', request, view, obj) for perm in perms)
            return result
    return AnyPerm


def All(*perms: Type[BasePermission]) -> Type[ComboPermission]:
    perms = [perm() for perm in perms]

    class AllPerms(ComboPermission):

        def has_permission(self, request, view):
            return all(self.run_check(perm, 'has_permission', request, view) for perm in perms)

        def has_object_permission(self, request, view, obj):
            result = all(self.run_check(perm, 'has_object_permission', request, view, obj) for perm in perms)
            return result
    return AllPerms


class CanComment(ComboPermission):
    """
    Checks to see if a user can comment or list comments on a particular object.
    """
    message = 'You are not allowed to comment on that.'

    def has_object_permission(self, request, view, obj):
        if not hasattr(obj, 'comment_permissions'):
            self.message = "That doesn't support comments."
            return False
        return all(
            (self.run_check(perm(), 'has_object_permission', request, view, obj) for perm in obj.comment_permissions)
        )


class CanListComments(ComboPermission):
    """
    Checks to see if a user can comment or list comments on a particular object.
    """
    message = 'You are not allowed to read comments on that.'

    def has_object_permission(self, request, view, obj):
        permissions_set = getattr(obj, 'comment_view_permissions', getattr(obj, 'comment_permissions', None))
        if permissions_set is None:
            self.message = "That doesn't support comments."
            return False
        return all(
            (self.run_check(perm(), 'has_object_permission', request, view, obj) for perm in permissions_set)
        )


# noinspection PyPep8Naming
def BlockedCheckPermission(ref_path=''):
    class WrappedBlockedPermission(BasePermission):
        def has_object_permission(self, request, view, obj):
            if not request.user.is_authenticated:
                # In any case where we care if the user is blocked, this is an action we don't want to offer anonymous
                # users access.
                return False
            path = ref_path.split('.')
            target = obj
            for segment in path:
                target = getattr(obj, segment)
            return not target.blocking.filter(id=request.user.id).exists()
    return WrappedBlockedPermission


class SessionKeySet(BasePermission):
    message = 'You do not have a session key set. Get a cookie first.'

    def has_permission(self, request: Request, view: View) -> bool:
        return bool(request.session.session_key)
