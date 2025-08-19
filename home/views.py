from django.shortcuts import render
import requests
from django.conf import settings
from django.db import DatabaseError # Import DatabaseError from Django
from datatime import datetime # Import current datetime.
# Display Restaurant name
def homepage_view(request):
    # Fetch name from settings.py in that already define.
   context ={
    'restaurant_name' : settings.RESTAURANT_NAME,
    'restaurant_phone': settings.RESTAURANT_PHONE,
    'year' : datetime.now().year
   }
   return render(request,'home/home.html',context)

# View for fetching API Response.
def menu_view(request):
    try:
        # Getting Response throught a URL.
        response = requests.get('http://localhost:8000/api/products/menu/')
        # Saving response in JSON format.
        menu_data = response.json()
    except DatabaseError:
        # If there's a database error, return empty data
        menu_data=[]
    except Exception:
        # Catching any other unexpected errors.
        menu_data=[]
        
    # Render data to frontend.
    return render(request, 'home/menu.html',{'menu':menu_data})

# 404 page
def trigger_404(request):
    return render(request,"404.html", status = 404)

# About page
def about_view(request):
    return render(request,'about.html')

# Contact page
def contact_us(request):
    return render(request,'contact.html')

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