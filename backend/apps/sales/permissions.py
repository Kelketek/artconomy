from typing import Any

from apps.profiles.models import UNSET, User
from apps.profiles.permissions import derive_user, staff_power
from apps.sales.constants import CONCURRENCY_STATUSES, LIMBO, MISSED
from apps.sales.utils import available_products_from_user
from django.db.models import Q
from django.utils import timezone
from django.views import View
from rest_framework.permissions import BasePermission
from rest_framework.request import Request


def derive_order(instance):
    from apps.sales.models import Deliverable, LineItem, Order

    if isinstance(instance, Order):
        return instance
    if isinstance(instance, LineItem):
        try:
            instance = instance.invoice.deliverables.get()
        except Deliverable.DoesNotExist:  # pragma: no cover
            return None
    if not isinstance(instance, Deliverable):  # pragma: no cover
        instance = instance.deliverable
    return instance.order


def derive_deliverable(instance):
    from apps.sales.models import Deliverable, LineItem

    if isinstance(instance, LineItem):
        try:
            instance = instance.invoice.deliverables.get()
        except Deliverable.DoesNotExist:  # pragma: no cover
            return None
    if not isinstance(instance, Deliverable):  # pragma: no cover
        instance = instance.deliverable
    return instance


class OrderViewPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        obj = derive_order(obj)
        if not obj:  # pragma: no cover
            return False
        if staff_power(request.user, "handle_disputes"):
            return True
        if staff_power(request.user, "table_seller"):
            return True
        if request.user == obj.buyer:
            return True
        if request.user == obj.seller:
            return True


class OrderSellerPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        obj = derive_order(obj)
        if not obj:  # pragma: no cover
            return False
        if staff_power(request.user, "handle_disputes"):
            return True
        if request.user == obj.seller:
            return True


class OrderBuyerPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        obj = derive_order(obj)
        if not obj:  # pragma: no cover
            return False
        if staff_power(request.user, "handle_disputes"):
            return True
        if request.user == obj.buyer:
            return True


class OrderPlacePermission(BasePermission):
    message = "This product is not available at this time."

    def has_object_permission(self, request, view, obj):
        if (
            not available_products_from_user(obj.user.artist_profile)
            .filter(id=obj.id)
            .exists()
        ):
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
        return obj.escrow_enabled


class EscrowDisabledPermission(BasePermission):
    """
    Only allow if Escrow is disabled on this order.
    """

    def has_object_permission(self, request, view, obj):
        return not obj.escrow_enabled


class RevisionsVisible(BasePermission):
    message = "Revisions are not visible yet."

    def has_object_permission(self, request, view, obj):
        return not obj.revisions_hidden


class BankingConfigured(BasePermission):
    message = (
        "You must have your banking settings configured before you can issue an "
        "invoice."
    )

    def has_object_permission(self, request, view, obj):
        return obj.artist_profile.bank_account_status is not UNSET


def DeliverableStatusPermission(
    *args, error_message="The deliverable is not in the right status for that."
):
    class StatusCheckPermission(BasePermission):
        message = error_message

        def has_object_permission(self, request, view, obj):
            from apps.sales.models import Deliverable, LineItem

            if isinstance(obj, LineItem):
                obj = obj.invoice.deliverables.get()
            if not isinstance(obj, Deliverable):  # pragma: no cover
                obj = obj.deliverable
            if obj.status in args:
                return True
            return False

    return StatusCheckPermission


class HasRevisionsPermission(BasePermission):
    message = "Revisions must be uploaded first."

    def has_object_permission(self, request, view, obj):
        return obj.revision_set.all().exists()


class OrderTimeUpPermission(BasePermission):
    message = "You may not dispute this order yet."

    def has_object_permission(self, request, view, obj):
        if obj.dispute_available_on and (
            obj.dispute_available_on > timezone.now().date()
        ):
            self.message = (
                "This order is not old enough to dispute. You can dispute it on "
                f"{obj.dispute_available_on}."
            )
            return False
        if not obj.dispute_available_on:  # pragma: no cover
            # Should never happen, because if this is a disputable status, this
            # timestamp should be set.
            return False
        return True


def LineItemTypePermission(
    *args, error_message="You are not permitted to edit line items of that type."
):
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
    message = (
        "You may only perform this action on deliverables without an associated "
        "product."
    )

    def has_object_permission(self, request, view, obj):
        deliverable = derive_deliverable(obj)
        if deliverable.product:
            return False
        return True


class ReferenceViewPermission(BasePermission):
    message = "You are not permitted to get that reference."

    def has_object_permission(self, request, view, obj):
        return obj.deliverables.filter(
            Q(order__buyer=request.user) | Q(order__seller=request.user)
        ).exists()


class LandscapeSellerPermission(BasePermission):
    message = "This feature only available to Landscape subscribers."

    def has_object_permission(self, request, view, obj):
        order = derive_order(obj)
        if not order:  # pragma: no cover
            return False
        return order.seller.landscape


class PublicQueue(BasePermission):
    message = "This queue is not public."

    def has_object_permission(self, request: Request, view: View, obj: User) -> bool:
        return obj.artist_profile.public_queue


def InvoiceStatus(*statuses):
    class InnerInvoiceStatus(BasePermission):
        message = "This invoice is not in the appropriate status for that action."

        def has_object_permission(self, request: Request, view: View, obj: Any) -> bool:
            invoice = getattr(obj, "invoice", obj)
            return invoice.status in statuses

    return InnerInvoiceStatus


def InvoiceType(*types):
    class InnerInvoiceType(BasePermission):
        message = "You may not perform this action on invoices of this type."

        def has_object_permission(self, request: Request, view: View, obj: Any) -> bool:
            invoice = getattr(obj, "invoice", obj)
            return invoice.type in types

    return InnerInvoiceType


class LimboCheck(BasePermission):
    message = "This deliverable is obscured from your view."

    def has_object_permission(self, request, view, obj):
        deliverable = derive_deliverable(obj)
        if not deliverable:  # pragma: no cover
            return False
        # This permission acts as a passthrough unless the user is the seller and this
        # is in limbo or missed.
        if not request.user == deliverable.order.seller:
            return True
        if deliverable.status in [LIMBO, MISSED]:
            return False
        return True


class PlanDeliverableAddition(BasePermission):
    message = (
        "Your current service plan does not support tracking more invoices. Please "
        "upgrade."
    )

    def has_object_permission(self, request, view, obj):
        from apps.sales.models import Deliverable

        user = derive_user(obj)
        max_orders = user.service_plan.max_simultaneous_orders
        if not user.service_plan.max_simultaneous_orders:
            return True
        if (
            Deliverable.objects.filter(
                order__seller=user, status__in=CONCURRENCY_STATUSES
            ).count()
            >= max_orders
        ):
            return False
        return True


class ValidPaypal(BasePermission):
    message = "No active PayPal configuration for this account."

    def has_object_permission(self, request, view, obj):
        from apps.sales.models import PaypalConfig

        user = derive_user(obj)
        try:
            user.paypal_config
        except PaypalConfig.DoesNotExist:
            return False
        return user.paypal_config.active
