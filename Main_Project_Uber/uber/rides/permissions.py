from rest_framework import permissions

class IsRideParticipant(permissions.BasePermission):
    """
    Custom permission to allow only the ride's rider or driver to mark payment.
    """

    def has_object_permission(self, request, view, obj):
        return request.user == getattr(obj.rider, "user", None) or \
               request.user == getattr(obj.driver, "user", None)
