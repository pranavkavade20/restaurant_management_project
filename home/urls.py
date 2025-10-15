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
    MenuCategoryViewSet,
    MenuItemViewSet,
    ContactCreateAPIView,
    AvailableTablesAPIView,
    TableDetailAPIView,
    TableListAPIView,
    DailySpecialsAPIView,
    UserReviewCreateView,
    MenuItemReviewListView,
    RestaurantInfoView,
    EmailValidationView,
    MenuCategoryListView,
)

# DRF Router for ViewSets
router = DefaultRouter()
router.register(r"menu-items", MenuItemViewSet, basename="menu-items")
router.register(r'categories', MenuCategoryViewSet, basename='menu-category')
urlpatterns = [
    # Web Views
    path("", homepage_view, name="home"),
    path("menu/", menu_view, name="menu"),
    path("about/", about_view, name="about"),
    path("contact/", contact_view, name="contact"),
    path("reservations/", reservations_view, name="reservations"),
    path("feedback/", feedback_view, name="feedback"),
    path('restaurant/info/', RestaurantInfoView.as_view(), name='restaurant-info'),

    # Custom 404 page (for testing)
    path("404-test/", custom_404_view, name="trigger_404"),

    # API Endpoints
    path("api/", include(router.urls)),
    
    path("api/contact/", ContactCreateAPIView.as_view(), name="api-contact"),
    path("api/tables/available/", AvailableTablesAPIView.as_view(), name="available_tables_api"),

    path("api/tables/", TableListAPIView.as_view(), name="table-list"),
    path("api/tables/<int:pk>/", TableDetailAPIView.as_view(), name="table-detail"),
     # 🔹 New Daily Specials API endpoint
    path("api/daily-specials/", DailySpecialsAPIView.as_view(), name="daily_specials_api"),

     # Create a new review for a specific menu item
    path(
        "api/menu/<int:menu_item_id>/reviews/add/",
        UserReviewCreateView.as_view(),
        name="add_menu_item_review"
    ),

    # Get all reviews for a specific menu item
    path(
        "api/menu/<int:menu_item_id>/reviews/",
        MenuItemReviewListView.as_view(),
        name="menu_item_reviews"
    ),
    path("validate-email/", EmailValidationView.as_view(), name="validate-email"),
    path("categories/", MenuCategoryListView.as_view(), name="menu-category-list"),
]
