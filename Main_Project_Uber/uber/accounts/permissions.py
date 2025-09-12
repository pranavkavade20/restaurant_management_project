from rest_framework.permissions import BasePermission


class IsRider(BasePermission):
    """
    Allows access only to users who have a Rider profile.
    Expects a OneToOne relation user.rider_profile (named as in models).
    """

    def has_permission(self, request, view):
        return hasattr(request.user, "rider_profile")


class IsDriver(BasePermission):
    """
    Allows access only to users who have a Driver profile.
    Expects a OneToOne relation user.driver_profile (named as in models).
    """

    def has_permission(self, request, view):
        return hasattr(request.user, "driver_profile")
