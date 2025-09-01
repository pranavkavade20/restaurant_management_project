from django.shortcuts import render, redirect
from django.conf import settings
from datetime import datetime
from django.contrib import messages
from .forms import FeedbackForm, ContactForm,Address
from products.models import MenuItem
from django.core.mail import send_mail
# from django.db import DatabaseError  # Import DatabaseError from Django
# # View for fetching API Response (with DB error handling)
# def menu_view(request):
#     try:
#         # Getting Response through a URL
#         response = requests.get('http://localhost:8000/api/products/menu/')
#         menu_data = response.json()
#     except DatabaseError:
#         # If there's a database error, return empty data
#         menu_data = []
#     except Exception:
#         # Catch any other unexpected errors
#         menu_data = []

#     # Render data to frontend
#     return render(request, 'home/menu.html', {'menu': menu_data})

# Display Restaurant name
def homepage_view(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("home")  # replace with your url name for homepage
    else:
        form = ContactForm()
    # Get the latest location (you can also use .all() if multiple locations)
    location = Address.objects.last()
    context = {
        'restaurant_name': settings.RESTAURANT_NAME,
        'restaurant_phone': settings.RESTAURANT_PHONE,
        'year': datetime.now().year,
        'form': form,  # pass form to template
        'location': location
    }
    return render(request, 'home/home.html', context)

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
Message:
{contact.message}

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

