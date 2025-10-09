from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    cart_view,
    add_to_cart,
    update_cart,
    remove_from_cart,
    CouponValidationView,
    OrderViewSet,
    UpdateOrderStatusAPIView,
)

# DRF Router for Orders API
router = DefaultRouter()
router.register(r"orders", OrderViewSet, basename="orders")

urlpatterns = [
    # ==========================
    # Web Routes (Cart Operations)
    # ==========================
    path("cart/", cart_view, name="cart"),
    path("cart/add/<int:item_id>/", add_to_cart, name="add_to_cart"),
    path("cart/update/<int:item_id>/", update_cart, name="update_cart"),
    path("cart/remove/<int:item_id>/", remove_from_cart, name="remove_from_cart"),

    # ==========================
    # API Routes (Orders & Coupons)
    # ==========================
    path("api/", include(router.urls)),
    path("api/coupon/validate/", CouponValidationView.as_view(), name="coupon-validate"),
    path("update-status/",UpdateOrderStatusAPIView.as_view(), name="update_order_status_api"),
]
