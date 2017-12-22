from logging import getLogger

from rest_framework.permissions import BasePermission, SAFE_METHODS

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
    message = "You do not have permission to comment on this topic."

    def has_object_permission(self, request, view, obj):
        # Jump to the top of the thread.
        while obj.parent:
            obj = obj.parent
        if obj.content_object is None:
            # Can't comment on something which doesn't exist. Also, log this.
            logger.debug("Attempted to comment on non-existent object. Comment ID was %s", obj.id)
            return False
        if request.user.is_staff:
            return True
        if not hasattr(obj.content_object, 'comment_permissions'):
            return False
        target = obj.content_object
        if not all((perm().has_object_permission(request, view, target) for perm in target.comment_permissions)):
            return False
        return True


class CommentDepthPermission(BasePermission):
    message = 'Comments are limited to top-level threads.'

    def has_object_permission(self, request, view, obj):
        # Limit comment depth for now.
        if obj.parent and obj.parent.parent:
            return False
        return True


# Use CamelCase since it outputs custom class.
def ObjectStatus(status, message):
    class PermClass(BasePermission):
        def has_object_permission(self, request, view, obj):
            if obj.status == self.status:
                return True
            return False

    # Scoping doesn't work when assigning in the definition.
    PermClass.status = status
    PermClass.message = message

    return PermClass


class IsStaff(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.is_staff


class IsSafeMethod(BasePermission):
    """
    Is a read-only request.
    """

    def has_permission(self, request, view):
        return request.method in SAFE_METHODS

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


def Any(perms):
    perms = [perm() for perm in perms]

    class AnyPerm(BasePermission):
        def has_object_permission(self, request, view, obj):
            return any(perm.has_object_permission(request, view, obj) for perm in perms)
    return AnyPerm


def All(perms):
    perms = [perm() for perm in perms]

    class AllPerms(BasePermission):
        def has_object_permission(self, request, view, obj):
            return all(perm.has_object_permission(request, view, obj) for perm in perms)
    return AllPerms
