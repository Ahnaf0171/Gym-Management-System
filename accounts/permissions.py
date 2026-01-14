from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied


def role_required(*allowed_roles):
    
    class RolePermission(BasePermission):
        def has_permission(self, request, view):
            if not request.user or not request.user.is_authenticated:
                return False
            if request.user.role in allowed_roles:
                return True
            raise PermissionDenied("You do not have permission to perform this action.")
    return RolePermission
