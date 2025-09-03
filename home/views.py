from django.shortcuts import render, redirect
from django.conf import settings
from datetime import datetime
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
            return redirect("home")  # replace with your url name for homepage
    else:
        form = ContactForm()
    
    # Search code
    query = request.GET.get("q", "")
    menu_items = MenuItem.objects.all()

    if query:
        menu_items = menu_items.filter(name__icontains=query)  # case-insensitive search
    restaurant = Restaurant.objects.first()  # Assuming single restaurant data
    context = {
        "restaurant_name": restaurant.name if restaurant else "Our Restaurant",
        "restaurant_phone": restaurant.phone if restaurant else "+91-0000000000",
        "restaurant_address": restaurant.address if restaurant else "Address not available",
        "restaurant": restaurant,
        "menu_items": menu_items,
        "query": query,
    }
    return render(request, "home/home.html", context)

def menu_view(request):
    menu_items = MenuItem.objects.all()
    return render(request, "home/menu.html", {"menu": menu_items})

# 404 page
def trigger_404(request):
    return render(request, "404.html", status=404)

# About page
def about_view(request):
    return render(request, 'about.html')

def contact(request):
    success = False
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = form.save()  # store in DB too

            # Send email notification
            subject = f"📩 New Contact Message from {contact.name}"
            message = f"""
                            You have received a new contact form submission.

                            Name: {contact.name}
                            Email: {contact.email}
                            Message:{contact.message}

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
            return redirect("contact")  # redirect to clear form
    else:
        form = ContactForm()

    return render(request, "contact.html", {
        "form": form,
        "restaurant_name": "Swaadify",
        "success": success
    })


# Reservation page
def reservations(request):
    context = {
        'restaurant_name': settings.RESTAURANT_NAME,
        'restaurant_phone': settings.RESTAURANT_PHONE
    }
    return render(request, "home/reservations.html", context)

# Feedback page
def feedback_view(request):
    if request.method == "POST":
        form = FeedbackForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Thanks for your feedback! ❤️")
            return redirect("feedback")  # back to the same page clean
    else:
        form = FeedbackForm()

    return render(request, "home/feedback.html", {"form": form})

