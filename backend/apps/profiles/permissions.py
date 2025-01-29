from typing import TYPE_CHECKING, Iterable

from dateutil.relativedelta import relativedelta
from django.utils import timezone
from django.views import View
from rest_framework.permissions import BasePermission
from rest_framework.request import Request

from apps.profiles.constants import POWER

if TYPE_CHECKING:
    from apps.sales.models import Invoice
    from apps.profiles.models import User


class ObjectControls(BasePermission):
    """
    Checks to make sure a user has permission to edit this object.
    """

    message = "You are not authorized to edit this."

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            # Superusers always have control.
            return True
        user = getattr(obj, "user", obj)
        if user == request.user:
            return True
        if hasattr(obj, "owner"):
            if obj.owner == request.user:
                return True


class SharedWith(BasePermission):
    """
    Checks to make sure a user has permission to view a particular submission.
    """

    def has_object_permission(self, request, view, obj):
        if not obj.private:
            return True
        if request.user.is_authenticated:
            if obj.shared_with.filter(id=request.user.id).exists():
                return True
        return False


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

    message = "Tagging is disabled for that submission."

    def has_object_permission(self, request, view, obj):
        if staff_power(request.user, "moderate_content"):
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
        if staff_power(request.user, "moderate_content") or staff_power(
            request.user, "view_as"
        ):
            return True
        if obj.owner == request.user:
            return True
        if not obj.private:
            return True
        if request.user.is_authenticated:
            if obj.shared_with.filter(id=request.user.id).exists():
                return True
        return False


class SubmissionCommentPermission(BasePermission):
    """
    Checks to see if comments are disabled for an submission.
    """

    def has_object_permission(self, request, view, obj):
        if obj.comments_disabled:
            return False
        if obj.owner.blocking.filter(id=request.user.id).exists() and not staff_power(
            request.user, "moderate_discussion"
        ):
            return False
        return True


def derive_user(obj):
    from apps.profiles.models import User

    if isinstance(obj, User):
        return obj
    return getattr(obj, "user", getattr(obj, "bill_to", getattr(obj, "owner", None)))


class IssuedBy(BasePermission):
    def has_object_permission(
        self, request: Request, view: View, obj: "Invoice"
    ) -> bool:
        invoice = getattr(obj, "invoice", obj)
        return invoice.issued_by == request.user


class BillTo(BasePermission):
    def has_object_permission(
        self, request: Request, view: View, obj: "Invoice"
    ) -> bool:
        invoice = getattr(obj, "invoice", obj)
        return invoice.bill_to == request.user


class NonPrivate(BasePermission):
    """
    Checks to see whether this object has its private field set True.
    """

    def has_object_permission(self, request, view, obj):
        return not obj.private


class ColorControls(BasePermission):
    """
    Checks to see whether this is a staffer or the color belongs to a character the user
    owns.
    """

    def has_object_permission(self, request, view, obj):
        if staff_power(request.user, "moderate_content"):
            return True
        if hasattr(obj, "user"):
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
        if staff_power(request.user, "view_as"):
            return True
        if obj.favorites_hidden:
            return False
        return True


class MessageReadPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        # These are private messages. Unless there's a real need let's keep this to
        # Superusers for now.
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
    message = "You may not comment on this journal."

    def has_object_permission(self, request, view, obj):
        if obj.comments_disabled:
            self.message = "Comments are disabled on this journal."
            return False
        if staff_power(request.user, "moderate_discussion"):
            return True
        if obj.user.blocking.filter(id=request.user.id):
            return False
        return True


class IsSuperuser(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class IsRegistered(BasePermission):
    message = "This action only available to registered users."

    def has_object_permission(self, request, view, obj):
        return request.user.is_registered

    def has_permission(self, request, view):
        return request.user.is_registered


def AccountAge(delta: relativedelta):
    class AccountAgePermission(BasePermission):
        message = "Your account is too new. Please try again later."

        def has_permission(self, request: Request, view: View) -> bool:
            if not request.user.is_registered:
                return False
            return request.user.date_joined < (timezone.now() - delta)

    return AccountAgePermission


class AccountCurrentPermission(BasePermission):
    message = "You have an outstanding subscription invoice which must be paid first."

    def has_object_permission(self, request, view, obj):
        user = derive_user(obj)
        return not user.delinquent


def staff_power(user: "User", *powers: Iterable["POWER"]):
    """
    Return true if this user is a staffer and has the specified power.
    """
    if user.is_superuser:
        return True
    if not hasattr(user, "staff_powers"):
        return False
    if not user.is_staff:
        return False
    return all((getattr(user.staff_powers, power) for power in powers))


class SocialsVisible(BasePermission):
    """
    Return True if the 'display_socials' flag is true.
    """

    message = "This user hasn't made their social links visible."

    def has_object_permission(self, request, view, obj):
        obj = derive_user(obj)
        if not hasattr(obj, "social_settings"):
            return False
        return obj.social_settings.display_socials
