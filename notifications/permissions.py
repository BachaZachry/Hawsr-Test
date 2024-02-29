from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    """
    Permission class for admin users
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_staff)
