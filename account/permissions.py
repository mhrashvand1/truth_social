from djoser.permissions import CurrentUserOrAdmin
from rest_framework.permissions import IsAuthenticated, BasePermission


class UserRetrievePermissions(IsAuthenticated):
    pass

class UserUpdatePermissions(BasePermission):
    def has_permission(self, request, view):
        return False
    
