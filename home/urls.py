from django.urls import path
from .views import *

urlpatterns = [
    path('', menu_view, name='home'),
    path('menu/' menu_view,name='menu'),
    path('404-test/',views.trigger_404)
]