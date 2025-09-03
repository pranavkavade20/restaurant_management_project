from django.urls import path
from .views import *
urlpatterns = [
    path('MenuItems/', MenuItemView.as_view(), name='MenuItem-list'),
    # path('menu/', get_menu, name='get_menu')
]