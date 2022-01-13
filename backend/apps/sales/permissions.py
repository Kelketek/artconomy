from typing import Any

from django.db.models import Q
from django.utils import timezone
from django.views import View
from rest_framework.permissions import BasePermission
from rest_framework.request import Request

from apps.profiles.models import UNSET, User
from apps.sales.utils import available_products_from_user


def derive_order(instance):
    from apps.sales.models import Order, Deliverable, LineItem
    if isinstance(instance, Order):
        return instance
    if isinstance(instance, LineItem):
        instance = instance.invoice.deliverables.get()
    if not isinstance(instance, Deliverable):
        instance = instance.deliverable
    return instance.order


class OrderViewPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        from apps.sales.models import Order
        obj = derive_order(obj)
        if not isinstance(obj, Order):
            obj = obj.order
        if request.user.is_staff:
            return True
        if request.user == obj.buyer:
            return True
        if request.user == obj.seller:
            return True


class OrderSellerPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        obj = derive_order(obj)
        if request.user.is_staff:
            return True
        if request.user == obj.seller:
            return True


class OrderBuyerPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        from apps.sales.models import Order
        obj = derive_order(obj)
        if request.user.is_staff:
            return True
        if request.user == obj.buyer:
            return True


class OrderPlacePermission(BasePermission):
    message = 'This product is not available at this time.'
    def has_object_permission(self, request, view, obj):
        if not available_products_from_user(obj.user.artist_profile).filter(id=obj.id).exists():
            return False
        if obj.user == request.user:
            self.message = 'You may not order your own product.'
            return False
        if not request.user.is_authenticated:
            return True
        # Need something a bit more robust here for guest checkout.
        if obj.user.artist_profile.user.blocking.filter(id=request.user.id).exists():
            return False
        return True


class EscrowPermission(BasePermission):
    """
    Only allow if Escrow is enabled on this order.
    """
    def has_object_permission(self, request, view, obj):
        if obj.escrow_disabled:
            return False
        return True


class EscrowDisabledPermission(BasePermission):
    """
    Only allow if Escrow is disabled on this order.
    """
    def has_object_permission(self, request, view, obj):
        if obj.escrow_disabled:
            return True
        return False


class RevisionsVisible(BasePermission):
    def has_object_permission(self, request, view, obj):
        return not obj.revisions_hidden


class BankingConfigured(BasePermission):
    message = 'You must have your banking settings configured before you can issue an invoice.'

    def has_object_permission(self, request, view, obj):
        return obj.artist_profile.bank_account_status is not UNSET


def DeliverableStatusPermission(*args, error_message='The deliverable is not in the right status for that.'):
    from apps.sales.models import Deliverable, LineItem
    class StatusCheckPermission(BasePermission):
        message = error_message
        def has_object_permission(self, request, view, obj):
            if isinstance(obj, LineItem):
                obj = obj.invoice.deliverables.get()
            if not isinstance(obj, Deliverable):
                obj = obj.deliverable
            if obj.status in args:
                return True
            return False
    return StatusCheckPermission


class HasRevisionsPermission(BasePermission):
    message = 'Revisions must be uploaded first.'
    def has_object_permission(self, request, view, obj):
        return obj.revision_set.all().exists()


class OrderTimeUpPermission(BasePermission):
    message = 'You may not dispute this order yet.'
    def has_object_permission(self, request, view, obj):
        if obj.dispute_available_on and (obj.dispute_available_on > timezone.now().date()):
            self.message = f'This order is not old enough to dispute. You can dispute it on {obj.dispute_available_on}.'
            return False
        if not obj.dispute_available_on:
            return False
        return True


class NoOrderOutput(BasePermission):
    message = 'You may not create a submission based on this deliverable.'
    def has_object_permission(self, request, view, obj):
        assert request.user
        if request.user not in [obj.order.seller, obj.order.buyer]:
            return False
        if obj.outputs.filter(owner=request.user).exists():
            self.message = 'You have already created a submission based on this deliverable.'
            return False
        return True


class PaidOrderPermission(BasePermission):
    message = 'You may not rate an order which was free.'
    def has_object_permission(self, request, view, obj):
        if obj.invoice.total().amount <= 0:
            return False
        return True


def LineItemTypePermission(*args, error_message='You are not permitted to edit line items of that type.'):
    """
    Verify that a line item is of a certain type.
    """
    class TypeCheckPermission(BasePermission):
        message = error_message
        def has_object_permission(self, request, view, obj):
            if obj.type in args:
                return True
            return False
    return TypeCheckPermission


class DeliverableNoProduct(BasePermission):
    message = 'You may only perform this action on deliverables without an associated product.'
    def has_object_permission(self, request, view, obj):
        from apps.sales.models import Deliverable, LineItem
        if isinstance(obj, LineItem):
            obj = obj.invoice.deliverables.get()
        if not isinstance(obj, Deliverable):
            obj = obj.deliverable
        if obj.product:
            return False
        return True


class ReferenceViewPermission(BasePermission):
    message = 'You are not permitted to get that reference.'
    def has_object_permission(self, request, view, obj):
        return obj.deliverables.filter(Q(order__buyer=request.user) | Q(order__seller=request.user)).exists()


class LandscapeSellerPermission(BasePermission):
    message = 'This feature only available to Landscape subscribers.'
    def has_object_permission(self, request, view, obj):
        return derive_order(obj).seller.landscape


class PublicQueue(BasePermission):
    message = 'This queue is not public.'

    def has_object_permission(self, request: Request, view: View, obj: User) -> bool:
        return obj.artist_profile.public_queue


def InvoiceStatus(*statuses):

    class InnerInvoiceStatus(BasePermission):
        message = 'This invoice is not in the appropriate status for that action.'

        def has_object_permission(self, request: Request, view: View, obj: Any) -> bool:
            invoice = getattr(obj, 'invoice', obj)
            return invoice.status in statuses

    return InnerInvoiceStatus
