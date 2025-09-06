from django.urls import path
from .views import RiderRegistrationView, DriverRegistrationView

urlpatterns = [
    path("register/rider/", RiderRegistrationView.as_view(), name="register-rider"),
    path("register/driver/", DriverRegistrationView.as_view(), name="register-driver"),
]
