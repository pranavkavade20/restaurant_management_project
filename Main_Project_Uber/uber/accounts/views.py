from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from django.db import transaction
from .serializers import RiderRegistrationSerializer, DriverRegistrationSerializer, UserSerializer,RiderLoginSerializer, DriverLoginSerializer,LogoutSerializer,RideRequestSerializer, RideSerializer
from .models import Ride
from .permissions import IsRider, IsDriver

class RiderRegistrationView(generics.GenericAPIView):
    """API endpoint for Rider registration."""
    serializer_class = RiderRegistrationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            rider = serializer.save()
            return Response(
                {
                    "message": "Rider registered successfully.",
                    "user": UserSerializer(rider.user).data,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DriverRegistrationView(generics.GenericAPIView):
    """API endpoint for Driver registration."""

    serializer_class = DriverRegistrationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            driver = serializer.save()
            return Response(
                {
                    "message": "Driver registered successfully.",
                    "user": UserSerializer(driver.user).data,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProtectedTestView(APIView):
    """A sample endpoint that requires JWT authentication."""

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        return Response(
            {
                "message": "You are successfully authenticated!",
                "user": request.user.username,
            }
        )




class RiderLoginView(TokenObtainPairView):
    """
    POST /api/auth/login/rider/
    Rider login endpoint that issues JWT tokens only if user is a Rider.
    """
    serializer_class = RiderLoginSerializer


class DriverLoginView(TokenObtainPairView):
    """
    POST /api/auth/login/driver/
    Driver login endpoint that issues JWT tokens only if user is a Driver.
    """
    serializer_class = DriverLoginSerializer

class RiderLogoutView(APIView):
    """
    POST /api/auth/logout/rider/
    Logs out a Rider by blacklisting their refresh token.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Rider logged out successfully."}, status=status.HTTP_205_RESET_CONTENT)


class DriverLogoutView(APIView):
    """
    POST /api/auth/logout/driver/
    Logs out a Driver by blacklisting their refresh token.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Driver logged out successfully."}, status=status.HTTP_205_RESET_CONTENT)



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
        serializer.save(rider=rider_profile, status=Ride.Status.REQUESTED)


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
