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

class IsRideRiderOrAssignedDriverOrStaff(BasePermission):
    """
    Allow access if:
    - Requesting user is the Rider who created the ride, OR
    - Requesting user is the Driver assigned to the ride, OR
    - Requesting user is staff (admin).
    """

    def has_object_permission(self, request, view, obj):
        user = request.user
        # staff bypass
        if user.is_staff:
            return True

        # rider owns the ride?
        if hasattr(user, "rider_profile") and obj.rider == user.rider_profile:
            return True

        # driver assigned to the ride?
        if hasattr(user, "driver_profile") and obj.driver == user.driver_profile:
            return True

        return False