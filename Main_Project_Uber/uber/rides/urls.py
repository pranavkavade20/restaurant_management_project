from django.urls import path
from .views import (
    RideRequestCreateView, 
    AvailableRidesListView,
    AcceptRideView,
    CompleteRideView,
    CancelRideView,
    RiderHistoryView, 
    DriverHistoryView,
    RideFeedbackCreateView,
    CalculateFareView,
    RidePaymentAPIView,
    DriverEarningsSummaryView,
    NearbyDriversView,
)
urlpatterns = [
    path("request/", RideRequestCreateView.as_view(), name="ride-request"),
    path("available/", AvailableRidesListView.as_view(), name="ride-available"),
    path("accept/<int:ride_id>/", AcceptRideView.as_view(), name="ride-accept"),
    path("complete/<int:ride_id>/", CompleteRideView.as_view(), name="ride-complete"),
    path("cancel/<int:ride_id>/", CancelRideView.as_view(), name="ride-cancel"),
    path("rider/history/", RiderHistoryView.as_view(), name="rider-history"),
    path("driver/history/", DriverHistoryView.as_view(), name="driver-history"),
    path("feedback/<int:ride_id>/", RideFeedbackCreateView.as_view(), name="ride-feedback"),
    path("calculate-fare/<int:ride_id>/", CalculateFareView.as_view(), name="calculate-fare"),
    path("payment/<int:pk>/", RidePaymentAPIView.as_view(), name="ride-payment"),
    path("driver/earnings/", DriverEarningsSummaryView.as_view(), name="driver-earnings"),
    path("nearby-drivers/", NearbyDriversView.as_view(), name="nearby-drivers"),
]
