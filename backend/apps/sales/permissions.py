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
