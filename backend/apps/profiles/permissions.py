from rest_framework.permissions import BasePermission


class ObjectControls(BasePermission):
    """
    Checks to make sure a user has permission to edit attributes of this character.
    """
    message = 'You are not authorized to edit this character.'

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        if obj.user == request.user:
            return True


class AssetControls(BasePermission):
    """
    Checks to make sure a user has permission to edit a particular asset.
    """

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        if obj.uploaded_by == request.user:
            return True


class AssetViewPermission(BasePermission):
    """
    Checks to make sure a user has permission to view a particular asset.
    """

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        if obj.uploaded_by == request.user:
            return True
        if obj.private:
            return False
        return True


class AssetCommentPermission(BasePermission):
    """
    Checks to see if comments are disabled for an asset.
    """
    def has_object_permission(self, request, view, obj):
        if obj.comments_disabled:
            return False
        return True


class UserControls(BasePermission):
    """
    Checks to see whether this is a staffer or the current user. Ignore actions if comment is deleted.
    """

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        if request.user == obj:
            return True
