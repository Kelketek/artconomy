from rest_framework.permissions import BasePermission


class ObjectControls(BasePermission):
    """
    Checks to make sure a user has permission to edit this object.
    """
    message = 'You are not authorized to edit this character.'

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        user = getattr(obj, 'user', obj)
        if user == request.user:
            return True
        if hasattr(obj, 'owner'):
            if obj.owner == request.user:
                return True


class SharedWith(BasePermission):
    """
    Checks to make sure a user has permission to view a particular asset.
    """

    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated:
            if obj.shared_with.filter(id=request.user.id).exists():
                return True
        if obj.private:
            return False
        return True


class AssetControls(BasePermission):
    """
    Checks to make sure a user has permission to edit a particular asset.
    """

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        if obj.owner == request.user:
            return True


class AssetViewPermission(BasePermission):
    """
    Checks to make sure a user has permission to view a particular asset.
    """

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        if obj.owner == request.user:
            return True
        if request.user.is_authenticated:
            if obj.shared_with.filter(id=request.user.id).exists():
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
        if obj.owner.blocking.filter(id=request.user.id).exists() and not request.user.is_staff:
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


class NonPrivate(BasePermission):
    """
    Checks to see whether this object has its private field set True.
    """
    def has_object_permission(self, request, view, obj):
        return not obj.private


class ColorControls(BasePermission):
    """
    Checks to see whether this is a staffer or the color belongs to a character the user owns.
    """

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        if hasattr(obj, 'user'):
            if request.user == obj.user:
                return True
            return False
        if request.user == obj.character.user:
            return True


class ColorLimit(BasePermission):
    def has_object_permission(self, request, view, obj):
        from .models import Character
        if obj.colors.all().count() < Character.colors__max:
            return True


class ViewFavorites(BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj == request.user:
            return True
        if request.user.is_staff:
            return True
        if obj.favorites_hidden:
            return False


class MessageReadPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        # These are private messages. Unless there's a real need let's keep this to Superusers for now.
        if request.user.is_superuser:
            return True
        if obj.sender == request.user and not obj.sender_left:
            return True
        if obj.recipients.all().filter(id=request.user.id):
            return True


class MessageControls(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user == obj.sender:
            return True
        if request.user.is_superuser:
            return True


class IsUser(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user == obj:
            return True
        if request.user.is_superuser:
            return True
