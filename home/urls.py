from django.urls import path
from .views import *

urlpatterns = [
    path('', menu_view, name='home'),
    path('menu/' menu_view, name='menu'),
    path('404-test/', trigger_404, name="trigger_404"),
    path('about/', about_view, name="about"),
    path('contact/', contact_us, name="contact"),
]