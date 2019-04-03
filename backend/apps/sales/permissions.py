from rest_framework.permissions import BasePermission


class OrderViewPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        if request.user == obj.buyer:
            return True
        if request.user == obj.seller:
            return True


class OrderSellerPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        if request.user == obj.seller:
            return True


class OrderBuyerPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        if request.user == obj.buyer:
            return True


class OrderPlacePermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj.hidden:
            return False
        if obj.user.blocking.filter(id=request.user.id).exists():
            return False
        if obj.user.commissions_disabled:
            return False
        if obj.user.commissions_closed:
            return False


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
    def has_permission(self, request, view):
        return request.user.bank_account_status is not None
