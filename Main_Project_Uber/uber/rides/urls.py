from django.urls import path
from .views import (
    RideRequestCreateView, 
    AvailableRidesListView,
    AcceptRideView,
    CompleteRideView,
    CancelRideView
)
urlpatterns = [
    path("request/", RideRequestCreateView.as_view(), name="ride-request"),
    path("available/", AvailableRidesListView.as_view(), name="ride-available"),
    path("accept/<int:ride_id>/", AcceptRideView.as_view(), name="ride-accept"),
    path("complete/<int:ride_id>/", CompleteRideView.as_view(), name="ride-complete"),
    path("cancel/<int:ride_id>/", CancelRideView.as_view(), name="ride-cancel"),
]
