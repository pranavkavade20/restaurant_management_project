# Built in modules
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

# Local Modules
from .models import Driver
from .serializers import ( 
    RiderRegistrationSerializer, 
    DriverRegistrationSerializer, 
    UserSerializer,
    RiderLoginSerializer, 
    DriverLoginSerializer,
    LogoutSerializer,
    DriverAvailabilitySerializer,
)

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

class DriverAvailabilityToggleView(APIView):
    """
    API endpoint for drivers to toggle availability (online/offline).
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # Ensure driver profile exists
        try:
            driver = request.user.driver_profile
        except Driver.DoesNotExist:
            return Response(
                {"detail": "Driver profile not found. Only drivers can toggle availability."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Validate and update availability
        serializer = DriverAvailabilitySerializer(
            instance=driver,
            data=request.data,
            context={"request": request},
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        updated_driver = serializer.save()

        return Response(
            {
                "message": "Availability updated successfully.",
                "is_available": updated_driver.availability_status,
            },
            status=status.HTTP_200_OK,
        )
