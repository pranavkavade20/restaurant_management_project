from django.urls import path
from .views import (
    RideRequestView,
    AvailableRidesView,
    AcceptRideView,
    UpdateDriverLocationView,
    TrackRideView,
    CompleteRideView,
    CancelRideView,
)

urlpatterns = [
    path("request/", RideRequestView.as_view(), name="ride-request"),
    path("available/", AvailableRidesView.as_view(), name="ride-available"),
    path("accept/<int:ride_id>/", AcceptRideView.as_view(), name="ride-accept"),
    path("update-location/", UpdateDriverLocationView.as_view(), name="ride-update-location"),
    path("track/<int:ride_id>/", TrackRideView.as_view(), name="ride-track"),
    path("complete/<int:ride_id>/", CompleteRideView.as_view(), name="ride-complete"),
    path("cancel/<int:ride_id>/", CancelRideView.as_view(), name="ride-cancel"),
]
