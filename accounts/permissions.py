from rest_framework.permissions import BasePermission


def role_required(*allowed_roles):
    
    class RolePermission(BasePermission):
        message = "You do not have permission to perform this action."
        
        def has_permission(self, request, view):
            if not request.user or not request.user.is_authenticated:
                return False 
            return request.user.role in allowed_roles

    return RolePermission