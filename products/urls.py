from django.urls import path
from .views import *
urlpatterns = [
    path('MenuItems/', MenuItemView.as_view(), name='MenuItem-list'),
    path("menu-items/by-category/", MenuItemsByCategoryAPIView.as_view(), name="menu-items-by-category"),
    path("menu-items/<int:pk>/update/", UpdateMenuItemAPIView.as_view(), name="update-menu-item"),
    path("menu-item/<int:pk>/availability/", MenuItemAvailabilityUpdateView.as_view(), name="menu-item-availability"),
]
