# Built in modules
from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db import transaction

# Accounts app
from accounts.permissions import IsRider, IsDriver,IsRideRiderOrAssignedDriverOrStaff
from accounts.models import Driver

# Ride app 
from .permissions import IsRideParticipant
from accounts.permissions import IsDriver
from .models import Ride, RideFeedback
from .serializers import (
            RideRequestSerializer, 
            RideSerializer,
            LocationUpdateSerializer, 
            RideTrackSerializer,
            RideHistorySerializer,
            RideFeedbackSerializer,
            FareCalculationSerializer,
            RidePaymentSerializer,
            DriverEarningsSummarySerializer,
    ) 

class RideRequestCreateView(generics.CreateAPIView):
    """
    POST /api/ride/request/
    Rider creates a new ride request. Rider must be authenticated and have a Rider profile.
    """
    serializer_class = RideRequestSerializer
    permission_classes = [IsAuthenticated, IsRider]

    def perform_create(self, serializer):
        """
        Attach the Rider profile to the Ride before saving.
        Assumes request.user has rider_profile (OneToOne).
        """
        rider_profile = self.request.user.rider_profile
        serializer.save(rider=rider_profile, status= Ride.Status.REQUESTED)

class AvailableRidesListView(generics.ListAPIView):
    """
    GET /api/ride/available/
    Drivers can query all rides in 'REQUESTED' status (i.e., unassigned).
    Permission: authenticated driver only.
    """
    serializer_class = RideSerializer
    permission_classes = [IsAuthenticated, IsDriver]

    def get_queryset(self):
        # Only rides that are REQUESTED and not assigned.
        return Ride.objects.filter(status=Ride.Status.REQUESTED, driver__isnull=True).order_by("requested_at")

class AcceptRideView(APIView):
    """
    POST /api/ride/accept/<ride_id>/
    Driver accepts a ride.
    - Only authenticated drivers may call.
    - Race-condition safe: uses select_for_update inside a transaction to ensure
      only one driver can successfully accept the ride.
    """
    permission_classes = [IsAuthenticated, IsDriver]

    def post(self, request, ride_id, *args, **kwargs):
        driver_profile = request.user.driver_profile

        # Wrap acceptance in atomic transaction to avoid race conditions.
        with transaction.atomic():
            # Lock the row for update to prevent concurrent acceptance
            try:
                ride = Ride.objects.select_for_update(nowait=False).get(pk=ride_id)
            except Ride.DoesNotExist:
                return Response({"detail": "Ride not found."}, status=status.HTTP_404_NOT_FOUND)

            if ride.status != Ride.Status.REQUESTED or ride.driver is not None:
                # Already accepted or no longer requestable
                return Response({"detail": "Ride already accepted or not available."}, status=status.HTTP_400_BAD_REQUEST)

            # Assign driver and change status
            ride.driver = driver_profile
            ride.status = Ride.Status.ONGOING
            ride.save(update_fields=["driver", "status", "updated_at"])

            serializer = RideSerializer(ride, context={"request": request})
            return Response({"message": "Ride accepted.", "ride": serializer.data}, status=status.HTTP_200_OK)

class DriverLocationUpdateView(APIView):
    """
    POST /api/ride/update-location/
    Endpoint for drivers to push latest GPS coords.
    - Requires authenticated driver (IsDriver).
    - Optionally accepts ride_id to validate that driver is working on that ride.
    """

    permission_classes = [IsAuthenticated, IsDriver]

    def post(self, request, *args, **kwargs):
        serializer = LocationUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        latitude = serializer.validated_data["latitude"]
        longitude = serializer.validated_data["longitude"]
        ride_id = serializer.validated_data.get("ride_id")

        driver_profile = request.user.driver_profile

        # If ride_id provided, perform sanity check: ride exists, is assigned to this driver, and is ONGOING
        if ride_id:
            ride = get_object_or_404(Ride, pk=ride_id)
            if ride.driver != driver_profile:
                return Response({"detail": "Driver not assigned to this ride."}, status=status.HTTP_403_FORBIDDEN)
            if ride.status != Ride.Status.ONGOING:
                return Response({"detail": "Ride is not ongoing; cannot update location for this ride."},
                                status=status.HTTP_400_BAD_REQUEST)

        # Persist latest coords to driver profile. Use a transaction in case other logic depends on it.
        with transaction.atomic():
            # Refresh from db to avoid overwriting concurrent updates
            Driver.objects.filter(pk=driver_profile.pk).update(
                current_latitude=latitude,
                current_longitude=longitude
            )

            # Optionally update ride's updated_at if ride provided (helps track last activity time)
            if ride_id:
                Ride.objects.filter(pk=ride_id).update(updated_at=ride.updated_at)  # touch updated_at via save below if needed

        return Response({"message": "Location updated."}, status=status.HTTP_200_OK)

class RideTrackView(APIView):
    """
    GET /api/ride/track/<ride_id>/
    Returns the latest known driver coordinates for the given ride.
    Access is limited to the rider who requested the ride, the assigned driver, or staff.
    Only returns data when ride.status == ONGOING (to protect privacy).
    """

    permission_classes = [IsAuthenticated, IsRideRiderOrAssignedDriverOrStaff]

    def get(self, request, ride_id, *args, **kwargs):
        ride = get_object_or_404(Ride, pk=ride_id)

        # Check permission object-level
        self.check_object_permissions(request, ride)

        # Only allow tracking while ride is ongoing
        if ride.status != Ride.Status.ONGOING:
            return Response({"detail": "Tracking available only for ongoing rides."}, status=status.HTTP_400_BAD_REQUEST)

        driver = ride.driver
        if driver is None:
            return Response({"detail": "No driver assigned yet."}, status=status.HTTP_404_NOT_FOUND)

        data = {
            "driver_latitude": driver.current_latitude,
            "driver_longitude": driver.current_longitude,
            "status": ride.status,
            "driver_id": driver.pk,
            "updated_at": ride.updated_at,
        }

        out = RideTrackSerializer(data).data
        return Response(out, status=status.HTTP_200_OK)

class CompleteRideView(APIView):
    """
    POST /api/ride/complete/<ride_id>/
    Allows the assigned driver to mark an ONGOING ride as COMPLETED.

    Rules enforced:
    - Requesting user must be authenticated and a Driver.
    - The driver must be the ride's assigned driver.
    - The ride must be in ONGOING status to be completed.
    - Uses an atomic select_for_update to avoid race conditions.
    """

    permission_classes = [IsAuthenticated, IsDriver]

    def post(self, request, ride_id, *args, **kwargs):
        driver_profile = request.user.driver_profile

        # Lock the ride row to avoid race conditions
        try:
            with transaction.atomic():
                ride = Ride.objects.select_for_update().get(pk=ride_id)
                # Existence check done; now validate ownership and status
                if ride.driver is None or ride.driver.pk != driver_profile.pk:
                    return Response(
                        {"error": "You are not assigned to this ride."},
                        status=status.HTTP_403_FORBIDDEN,
                    )

                if ride.status != Ride.Status.ONGOING:
                    return Response(
                        {"error": "Only ongoing rides can be marked as completed."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                # Transition to COMPLETED
                ride.status = Ride.Status.COMPLETED
                ride.save(update_fields=["status", "updated_at"])

                return Response({"message": "Ride marked as completed."}, status=status.HTTP_200_OK)

        except Ride.DoesNotExist:
            return Response({"error": "Ride not found."}, status=status.HTTP_404_NOT_FOUND)

class CancelRideView(APIView):
    """
    POST /api/ride/cancel/<ride_id>/
    Allows the rider who requested the ride to cancel it only when the ride is still REQUESTED.

    Rules enforced:
    - Requesting user must be authenticated and a Rider.
    - The rider must own the ride.
    - The ride must be in REQUESTED status to be cancelled.
    - Uses select_for_update inside a transaction to ensure state integrity.
    """

    permission_classes = [IsAuthenticated, IsRider]

    def post(self, request, ride_id, *args, **kwargs):
        rider_profile = request.user.rider_profile

        try:
            with transaction.atomic():
                ride = Ride.objects.select_for_update().get(pk=ride_id)

                if ride.rider.pk != rider_profile.pk:
                    return Response(
                        {"error": "You are not authorized to cancel this ride."},
                        status=status.HTTP_403_FORBIDDEN,
                    )

                if ride.status != Ride.Status.REQUESTED:
                    return Response(
                        {"error": "Cannot cancel a ride that is already ongoing or completed."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                # Transition to CANCELLED
                ride.status = Ride.Status.CANCELLED
                ride.save(update_fields=["status", "updated_at"])

                return Response({"message": "Ride cancelled successfully."}, status=status.HTTP_200_OK)

        except Ride.DoesNotExist:
            return Response({"error": "Ride not found."}, status=status.HTTP_404_NOT_FOUND)

def _get_rider_profile(user):
    """
    Helper: try common attribute names for rider profile.
    Returns the rider profile object or None.
    """
    return getattr(user, "rider_profile", None) or getattr(user, "rider", None)

def _get_driver_profile(user):
    """
    Helper: try common attribute names for driver profile.
    Returns the driver profile object or None.
    """
    return getattr(user, "driver_profile", None) or getattr(user, "driver", None)

class RiderHistoryView(generics.ListAPIView):
    """
    GET /api/rider/history/
    Returns completed and cancelled rides for the logged-in rider.
    Paginated (DRF PageNumberPagination, PAGE_SIZE in settings).
    """
    serializer_class = RideHistorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        rider = _get_rider_profile(self.request.user)
        if rider is None:
            # Not a rider account
            raise PermissionDenied(detail="Authenticated user is not a Rider.")
        # Only COMPLETED or CANCELLED rides for this rider
        return Ride.objects.filter(
            rider=rider,
            status__in=[Ride.Status.COMPLETED, Ride.Status.CANCELLED],
        ).order_by("-requested_at")

class DriverHistoryView(generics.ListAPIView):
    """
    GET /api/driver/history/
    Returns completed and cancelled rides for the logged-in driver.
    Paginated (DRF PageNumberPagination, PAGE_SIZE in settings).
    """
    serializer_class = RideHistorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        driver = _get_driver_profile(self.request.user)
        if driver is None:
            # Not a driver account
            raise PermissionDenied(detail="Authenticated user is not a Driver.")
        # Only COMPLETED or CANCELLED rides for this driver
        return Ride.objects.filter(
            driver=driver,
            status__in=[Ride.Status.COMPLETED, Ride.Status.CANCELLED],
        ).order_by("-requested_at")

def _get_rider_profile(user):
    """Helper: tolerant lookup for rider profile attribute names."""
    return getattr(user, "rider_profile", None) or getattr(user, "rider", None)


def _get_driver_profile(user):
    """Helper: tolerant lookup for driver profile attribute names."""
    return getattr(user, "driver_profile", None) or getattr(user, "driver", None)

class RideFeedbackCreateView(APIView):
    """
    POST /api/ride/feedback/<ride_id>/
    Allows the rider or the assigned driver to submit feedback once the ride is COMPLETED.

    Business rules enforced:
    - User must be authenticated.
    - Ride must exist and be COMPLETED.
    - User must be either the ride.rider or the ride.driver.
    - The user can submit feedback only once per role (driver/rider).
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, ride_id, *args, **kwargs):
        # Lock the ride row first to avoid race conditions where two parties submit simultaneously
        try:
            with transaction.atomic():
                ride = Ride.objects.select_for_update().get(pk=ride_id)
                # 1) Ride must be completed
                if ride.status != Ride.Status.COMPLETED:
                    return Response(
                        {"error": "Ride is not completed yet."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                user = request.user
                rider_profile = _get_rider_profile(user)
                driver_profile = _get_driver_profile(user)

                # 2) Determine whether the user is the rider or the assigned driver
                is_driver = False
                if driver_profile and ride.driver is not None and ride.driver.pk == driver_profile.pk:
                    is_driver = True
                elif rider_profile and ride.rider is not None and ride.rider.pk == rider_profile.pk:
                    is_driver = False
                else:
                    # User is not part of this ride
                    raise PermissionDenied(detail="You are not part of this ride.")

                # 3) Check feedback existence for this role (prevent duplicates early)
                if RideFeedback.objects.filter(ride=ride, is_driver=is_driver).exists():
                    return Response(
                        {"error": "You have already submitted feedback for this ride."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                # 4) Validate payload via serializer
                # Pass ride via context so serializer can validate using ride
                serializer = RideFeedbackSerializer(
                    data=request.data, context={"request": request, "ride": ride}
                )
                serializer.is_valid(raise_exception=True)

                # Serializer's create uses validated_data (which the serializer populates with ride, is_driver, submitted_by)
                feedback = serializer.save()

                return Response(
                    {"message": "Feedback submitted successfully."},
                    status=status.HTTP_201_CREATED,
                )

        except Ride.DoesNotExist:
            return Response({"error": "Ride not found."}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError as exc:
            # serializer validation errors or custom validation raising ValidationError
            return Response(exc.detail, status=status.HTTP_400_BAD_REQUEST)
        except PermissionDenied as exc:
            return Response({"error": str(exc.detail)}, status=status.HTTP_403_FORBIDDEN)

class CalculateFareView(APIView):
    """
    POST endpoint to calculate and store fare for a completed ride.
    Only accessible to the ride's rider, driver, or admin.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, ride_id):
        ride = get_object_or_404(Ride, id=ride_id)

        # ✅ Security: Only rider, driver, or admin can access
        user = request.user
        if not (user.is_staff or ride.rider.user == user or (ride.driver and ride.driver.user == user)):
            return Response(
                {"error": "You are not authorized to calculate fare for this ride."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # ✅ Ensure ride is completed
        if ride.status != Ride.Status.COMPLETED:
            return Response(
                {"error": "Ride must be completed before fare calculation."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ✅ Prevent recalculation if fare already set
        if ride.fare is not None:
            return Response(
                {"error": "Fare already set."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = FareCalculationSerializer(instance=ride, data={}, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {
                "fare": ride.fare,
                "message": "Fare calculated and saved.",
            },
            status=status.HTTP_200_OK,
        )

class RidePaymentAPIView(generics.GenericAPIView):
    """
    API endpoint to mark a ride as PAID with the chosen payment method.
    URL: PATCH /api/ride/payment/<ride_id>/

    Only PATCH is allowed for updates (REST-compliant).
    """

    queryset = Ride.objects.all()
    serializer_class = RidePaymentSerializer
    permission_classes = [IsAuthenticated, IsRideParticipant]
    lookup_url_kwarg = "pk"

    def patch(self, request, *args, **kwargs):
        ride = self.get_object()

        serializer = self.get_serializer(ride, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {
                "message": "Payment marked as complete.",
                "status": ride.payment_status,
                "method": ride.payment_method
            },
            status=status.HTTP_200_OK
        )

class DriverEarningsSummaryView(APIView):
    """
    API endpoint for drivers to fetch their 7-day earnings summary.
    """

    permission_classes = [IsAuthenticated, IsDriver]

    def get(self, request, *args, **kwargs):
        driver = request.user.driver_profile  # Driver profile linked to User
        serializer = DriverEarningsSummarySerializer.build_summary(driver)
        return Response(serializer.data, status=status.HTTP_200_OK)
