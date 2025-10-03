from django.urls import path
from .views import *

urlpatterns = [
    path('', homepage_view, name='home'),
    path('menu/', menu_view, name='menu'),
    path('404-test/',trigger_404, name= "trigger_404"),
    path('about/', about_view, name='about'),
    path("contact/", Contact.as_view(), name="contact"),
    path('reservations/', reservations, name='reservations'),
    path("feedback/",feedback_view, name="feedback"),
    path("categories/", MenuCategoryListView.as_view(), name="menu-category-list"),
    path("menu-items/", MenuItemViewSet.as_view({"get": "list"}), name="menu-items"),

]