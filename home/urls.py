from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    homepage_view,
    menu_view,
    about_view,
    contact_view,
    reservations_view,
    feedback_view,
    custom_404_view,
    MenuCategoryListView,
    MenuItemViewSet,
    ContactCreateAPIView,
    AvailableTablesAPIView,
    TableDetailAPIView,
    TableListAPIView,
)

# DRF Router for ViewSets
router = DefaultRouter()
router.register(r"menu-items", MenuItemViewSet, basename="menu-items")

urlpatterns = [
    # Web Views
    path("", homepage_view, name="home"),
    path("menu/", menu_view, name="menu"),
    path("about/", about_view, name="about"),
    path("contact/", contact_view, name="contact"),
    path("reservations/", reservations_view, name="reservations"),
    path("feedback/", feedback_view, name="feedback"),

    # Custom 404 page (for testing)
    path("404-test/", custom_404_view, name="trigger_404"),

    # API Endpoints
    path("api/", include(router.urls)),
    path("api/categories/", MenuCategoryListView.as_view(), name="menu-category-list"),
    path("api/contact/", ContactCreateAPIView.as_view(), name="api-contact"),
    path("api/tables/available/", AvailableTablesAPIView.as_view(), name="available_tables_api"),
    path("api/tables/", TableListAPIView.as_view(), name="table-list"),
    path("api/tables/<int:pk>/", TableDetailAPIView.as_view(), name="table-detail"),
]
