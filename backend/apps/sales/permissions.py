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
