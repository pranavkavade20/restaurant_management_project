from django.urls import path
from .views import *
urlpatterns = [
    path('MenuItems/', MenuItemView.as_view(), name='MenuItem-list'),
]
