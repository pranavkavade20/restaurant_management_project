from django.urls import path
from .views import (
    RideRequestCreateView, 
    AvailableRidesListView,
    AcceptRideView
)
urlpatterns = [
    path("ride/request/", RideRequestCreateView.as_view(), name="ride-request"),
    path("ride/available/", AvailableRidesListView.as_view(), name="ride-available"),
    path("ride/accept/<int:ride_id>/", AcceptRideView.as_view(), name="ride-accept"),
]
