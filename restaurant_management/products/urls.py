from django.urls import path
from .views import *
urlpatterns = [
    path('MenuItems/', MenuItemView.as_view(), name='MenuItem-list'),
    path("menu-items/by-category/", MenuItemsByCategoryAPIView.as_view(), name="menu-items-by-category"),
]
