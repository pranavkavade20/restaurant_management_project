# from django.db import DatabaseError # Import DatabaseError from Django
# import requests

from django.shortcuts import render
from django.conf import settings
from datatime import datetime # Import current datetime.
from products.models import MenuItem
from .forms import *
from django.contrib import messages

# Display Restaurant name
def homepage_view(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("home") # Render to homepage.
    else:
        form = ContactForm()
    # Fetch name from settings.py in that already define.
   context ={
    'restaurant_name' : settings.RESTAURANT_NAME,
    'restaurant_phone': settings.RESTAURANT_PHONE,
    'year' : datetime.now().year,
    'form' : form, # pass form to template
   }
   return render(request,'home/home.html',context)

# Below view is for testing.
# # View for fetching API Response.
# def menu_view(request):
#     try:
#         # Getting Response throught a URL.
#         response = requests.get('http://localhost:8000/api/products/menu/')
#         # Saving response in JSON format.
#         menu_data = response.json()
#     except DatabaseError:
#         # If there's a database error, return empty data
#         menu_data=[]
#     except Exception:
#         # Catching any other unexpected errors.
#         menu_data=[]
        
#     # Render data to frontend.
#     return render(request, 'home/menu.html',{'menu':menu_data})

# Newly created View for fetching Menu Items
def menu_view(request):
    menu_items = MenuItem.objects.all()
    return render(request,"home/menu.html", {"menu":menu_items})

# 404 page
def trigger_404(request):
    return render(request,"404.html", status = 404)

# About page
def about_view(request):
    return render(request,'about.html')

# Contact page
def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save() # Save submission to DB
            return redirect(contact) # Redirect to avoid resubmission
    else:
        form = ContactForm()
    return render(request,'contact.html',{"form": form, "restaurant_name": "Swaadify"})

# Reservation page
def reservations(request):
    # Fetch name from settings.py in that already define.
    context ={
    'restaurant_name' : settings.RESTAURANT_NAME,
    'restaurant_phone': settings.RESTAURANT_PHONE
    }
    return render(request,"home/reservations.html",context)

# Feedback page
def feedback_view(request):
    # Check the request is POST or not.
    if request.method =="POST":
        # Fetching form.
        form = FeedbackForm(request.POST)
        # Checking the form is valid.
        if form.is_valid():
            form.save() # Saving data of form.
            # Showing success message for user.
            messages.success(request,"Thanks for your feedback! ❤️")
            return redirect("feedback") # back to the same page clean
    else:
    # Else the method is not POST then give empty form to user.
        form = FeedbackForm()
    return render(request,"home/feedback.html",{"form":form})