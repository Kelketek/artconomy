from rest_framework.permissions import BasePermission


class ObjectControls(BasePermission):
    """
    Checks to make sure a user has permission to edit this object.
    """
    message = 'You are not authorized to edit this.'

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
    Checks to make sure a user has permission to view a particular submission.
    """

    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated:
            if obj.shared_with.filter(id=request.user.id).exists():
                return True
        if obj.private:
            return False
        return True


class SubmissionControls(BasePermission):
    """
    Checks to make sure a user has permission to edit a particular submission.
    """

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        if obj.owner == request.user:
            return True


class SubmissionTagPermission(BasePermission):
    """
    Checks if the user has the ability to tag a submission
    """
    message = 'Tagging is disabled for that submission.'
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        if obj.owner == request.user:
            return True
        if not request.user.is_authenticated:
            return False
        if not obj.owner.taggable:
            return False
        return True

class SubmissionViewPermission(BasePermission):
    """
    Checks to make sure a user has permission to view a particular submission.
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


class SubmissionCommentPermission(BasePermission):
    """
    Checks to see if comments are disabled for an submission.
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
        if hasattr(obj, 'user'):
            if obj.user == request.user:
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
        return True


class MessageReadPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        # These are private messages. Unless there's a real need let's keep this to Superusers for now.
        if request.user.is_superuser:
            return True
        if obj.participants.all().filter(id=request.user.id):
            return True


class IsUser(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user == obj:
            return True
        if request.user.is_superuser:
            return True


class IsSubject(BasePermission):
    def has_permission(self, request, view):
        if request.subject == request.user:
            return True
        if request.user.is_superuser:
            return True


class JournalCommentPermission(BasePermission):
    message = 'You may not comment on this journal.'

    def has_object_permission(self, request, view, obj):
        if obj.comments_disabled:
            self.message = 'Comments are disabled on this journal.'
            return False
        if obj.user.is_staff:
            return True
        if obj.user.blocking.filter(id=request.user.id):
            return False
        return True


class IsSuperuser(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        return False


class IsRegistered(BasePermission):
    message = 'This action only available to registered users.'
    def has_object_permission(self, request, view, obj):
        return request.user.is_registered

    def has_permission(self, request, view):
        return request.user.is_registered