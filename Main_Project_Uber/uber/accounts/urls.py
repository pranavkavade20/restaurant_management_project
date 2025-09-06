from django.urls import path
from .views import RiderRegistrationView, DriverRegistrationView, ProtectedTestView

urlpatterns = [
    path("register/rider/", RiderRegistrationView.as_view(), name="register-rider"),
    path("register/driver/", DriverRegistrationView.as_view(), name="register-driver"),
    path("protected/", ProtectedTestView.as_view(), name="protected-test"),
]
