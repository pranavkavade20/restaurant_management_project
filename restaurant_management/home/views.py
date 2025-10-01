# Built in modules
from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib import messages
# from django.core.mail import send_mail
from rest_framework.generics import ListAPIView
from rest_framework import viewsets, filters
from rest_framework.pagination import PageNumberPagination

# Local modules
from products.models import MenuItem
from .forms import *
from .models import MenuCategory
from .serializers import MenuCategorySerializer,MenuItemSerializer

from rest_framework import generics, status
from rest_framework.response import Response
from .models import Contact
from .serializers import ContactSerializer

# Display Restaurant name
def homepage_view(request):
    # # Contact form on homepage
    # if request.method == "POST":
    #     form = ContactForm(request.POST)
    #     if form.is_valid():
    #         form.save()
    #         return redirect("home")  # replace with your url name for homepage
    # else:
    #     form = ContactForm()
    
    # Search code
    query = request.GET.get("q", "")
    menu_items = MenuItem.objects.all()
    if query:
        menu_items = menu_items.filter(name__icontains=query)  # case-insensitive search
    restaurant = Restaurant.objects.first()  # Assuming single restaurant data
    
    # Initialize cart in session if not already present
    if 'cart' not in request.session:
        request.session['cart'] = {}

    # Count total items in the cart
    cart = request.session['cart']
    total_items = sum(cart.values())
    context = {
        "restaurant_name": restaurant.name if restaurant else "Our Restaurant",
        "restaurant_phone": restaurant.phone if restaurant else "+91-0000000000",
        "restaurant_address": restaurant.address if restaurant else "Address not available",
        "restaurant": restaurant,
        "menu_items": menu_items,
        "query": query,
        'total_items': total_items,
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

# def contact(request):
#     success = False
#     if request.method == "POST":
#         form = ContactForm(request.POST)
#         if form.is_valid():
#             contact = form.save()  # store in DB too

#             # Send email notification
#             subject = f"📩 New Contact Message from {contact.name}"
#             message = f"""
#                             You have received a new contact form submission.

#                             Name: {contact.name}
#                             Email: {contact.email}
#                             Message:{contact.message}

#                             -- Swaadify Contact Form
#                             """
#             send_mail(
#                 subject,
#                 message,
#                 settings.DEFAULT_FROM_EMAIL,
#                 [settings.RESTAURANT_EMAIL],
#                 fail_silently=False,
#             )

#             success = True
#             return redirect("contact")  # redirect to clear form
#     else:
#         form = ContactForm()

#     return render(request, "contact.html", {
#         "form": form,
#         "restaurant_name": "Swaadify",
#         "success": success
#     })

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

class MenuCategoryListView(ListAPIView):
    """
    API endpoint to list all menu categories.
    """
    queryset = MenuCategory.objects.all().order_by('name')
    serializer_class = MenuCategorySerializer

class MenuItemPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class MenuItemViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint to list and search menu items by name.
    """
    queryset = MenuItem.objects.all().order_by("name")
    serializer_class = MenuItemSerializer
    pagination_class = MenuItemPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ["name"]

class Contact(generics.CreateAPIView):
    """
    API endpoint to handle contact form submissions.
    Accepts POST requests with name, email, and message.
    Stores submissions in the database after validation.
    """
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return Response(
            {
                "message": "Your contact form has been submitted successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )


from .utils import send_email_async

async def contact_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        subject = f"New Contact Message from {name}"
        body = f"Name: {name}\nEmail: {email}\nMessage: {message}"
        recipient = ['admin@example.com']  # Your admin/support email

        email_sent = await send_email_async(subject, body, recipient)

        if email_sent:
            return render(request, 'home/contact_success.html')
        else:
            return render(request, 'home/contact_failure.html')

    return render(request, 'home/contact.html')

