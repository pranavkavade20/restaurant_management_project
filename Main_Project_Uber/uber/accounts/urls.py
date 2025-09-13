from django.urls import path
from .views import (
    RiderRegistrationView, 
    DriverRegistrationView,  
    RiderLoginView, 
    DriverLoginView,
    RiderLogoutView, 
    DriverLogoutView, 
    ProtectedTestView,
)
urlpatterns = [
    path("register/rider/", RiderRegistrationView.as_view(), name="register-rider"),
    path("register/driver/", DriverRegistrationView.as_view(), name="register-driver"),
    path("auth/login/rider/", RiderLoginView.as_view(), name="rider-login"),
    path("auth/login/driver/", DriverLoginView.as_view(), name="driver-login"),
    path("auth/logout/rider/", RiderLogoutView.as_view(), name="rider-logout"),
    path("auth/logout/driver/", DriverLogoutView.as_view(), name="driver-logout"),
    path("protected/", ProtectedTestView.as_view(), name="protected-test"),
]
