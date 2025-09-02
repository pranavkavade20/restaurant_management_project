# from django.db import DatabaseError # Import DatabaseError from Django
# import requests
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

from django.shortcuts import render,redirect
from django.conf import settings
from datatime import datetime       # Import current datetime.
from django.contrib import messages
from django.core.mail import send_mail
from products.models import MenuItem
from .forms import *


# Display Restaurant name
def homepage_view(request):
    # Contact form on homepage
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("home") # Render to homepage.
    else:
        form = ContactForm()
    # Search code
    query = request.GET.get("q","")
    menu_items = MenuItem.objects.all()

    if query:
        menu_items = menu_items.filter(name_icontains=query) #case-insernsitive search 
    restaurant = Restaurant.objects.first() # Assuming single restaurant data
    context = {
        "restaurant_name": restaurant.name if restaurant else "Our Restaurant",
        "restaurant_phone": restaurant.phone if restaurant else "+91 0000000000",
        "restaurant_address": restaurant.address if restaurant else "Address not available",
        "restaurant": restaurant,
        "menu_items": menu_items,
        "query":query
    }
    return render(request,"home/home.html", context)

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

"""
This contact page and email now is show on terminal.
But in production we replace with restaurant email.
"""
def contact(request):
    success = False
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save() # Save submission to DB
            subject =f"📩 New Contact Message from {contact.name}"
            message = f"""
                        You have recevied a new contact form submission.
                        
                        Name: {contact.name}
                        Email: {contact.email}
                        Message : {contact.message}

                        -- Swaadify Contact Form            
            """
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [settings.RESTAURANT_EMAIL],
                fail_silently=False,
            )
            success = True
            return redirect(contact) # Redirect to clear form.
    else:
        form = ContactForm()
    return render(request,'contact.html',{
        "form": form, 
        "restaurant_name": "Swaadify",
        "success": success
    })

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