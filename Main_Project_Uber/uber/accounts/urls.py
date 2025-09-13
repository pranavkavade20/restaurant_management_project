from django.urls import path
from .views import RiderRegistrationView, DriverRegistrationView,  RiderLoginView, DriverLoginView,RiderLogoutView, DriverLogoutView, ProtectedTestView,RideRequestCreateView, AvailableRidesListView,AcceptRideView,DriverLocationUpdateView, RideTrackView

urlpatterns = [
    path("register/rider/", RiderRegistrationView.as_view(), name="register-rider"),
    path("register/driver/", DriverRegistrationView.as_view(), name="register-driver"),
    path("auth/login/rider/", RiderLoginView.as_view(), name="rider-login"),
    path("auth/login/driver/", DriverLoginView.as_view(), name="driver-login"),
    path("auth/logout/rider/", RiderLogoutView.as_view(), name="rider-logout"),
    path("auth/logout/driver/", DriverLogoutView.as_view(), name="driver-logout"),
    path("protected/", ProtectedTestView.as_view(), name="protected-test"),
    path("ride/request/", RideRequestCreateView.as_view(), name="ride-request"),
    path("ride/available/", AvailableRidesListView.as_view(), name="ride-available"),
    path("ride/accept/<int:ride_id>/", AcceptRideView.as_view(), name="ride-accept"),
    path("ride/update-location/", DriverLocationUpdateView.as_view(), name="ride-update-location"),
    path("ride/track/<int:ride_id>/", RideTrackView.as_view(), name="ride-track"),
]
