from rest_framework import status, generics
from rest_framework.response import Response
from .serializers import RiderRegistrationSerializer, DriverRegistrationSerializer, UserSerializer


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
