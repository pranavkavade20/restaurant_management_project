from django.urls import path
from .views import (
    RiderRegisterView,
    DriverRegisterView,
    RiderLoginView,
    DriverLoginView,
    LogoutView,
)

urlpatterns = [
    path("register/rider/", RiderRegisterView.as_view(), name="register-rider"),
    path("register/driver/", DriverRegisterView.as_view(), name="register-driver"),
    path("login/rider/", RiderLoginView.as_view(), name="login-rider"),
    path("login/driver/", DriverLoginView.as_view(), name="login-driver"),
    path("logout/", LogoutView.as_view(), name="logout"),
]
