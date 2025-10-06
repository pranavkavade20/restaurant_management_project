# Built-in modules
from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib import messages

# Django REST Framework modules
from rest_framework import viewsets, generics, status, filters
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.generics import ListAPIView

# Local modules
from .forms import ContactForm, FeedbackForm
from .models import MenuCategory, Contact
from .serializers import MenuCategorySerializer, MenuItemSerializer, ContactSerializer
from .utils import send_email_async
from products.models import MenuItem
from .models import Restaurant  # assuming Restaurant model exists


# ==========================
# Web Views
# ==========================

def homepage_view(request):
    """Display the homepage with menu search and restaurant details."""
    query = request.GET.get("q", "")
    menu_items = MenuItem.objects.filter(name__icontains=query) if query else MenuItem.objects.all()
    restaurant = Restaurant.objects.first()

    # Initialize or read cart from session
    cart = request.session.get('cart', {})
    request.session['cart'] = cart
    total_items = sum(cart.values())

    context = {
        "restaurant": restaurant,
        "restaurant_name": restaurant.name if restaurant else "Our Restaurant",
        "restaurant_phone": restaurant.phone if restaurant else "+91-0000000000",
        "restaurant_address": restaurant.address if restaurant else "Address not available",
        "menu_items": menu_items,
        "query": query,
        "total_items": total_items,
    }
    return render(request, "home/home.html", context)


def menu_view(request):
    """Display the complete menu."""
    menu_items = MenuItem.objects.all()
    return render(request, "home/menu.html", {"menu": menu_items})


def about_view(request):
    """Display the about page."""
    return render(request, "about.html")


def reservations_view(request):
    """Display the reservations page."""
    context = {
        'restaurant_name': getattr(settings, 'RESTAURANT_NAME', 'Our Restaurant'),
        'restaurant_phone': getattr(settings, 'RESTAURANT_PHONE', '+91-0000000000'),
    }
    return render(request, "home/reservations.html", context)


def feedback_view(request):
    """Handle feedback form submission."""
    if request.method == "POST":
        form = FeedbackForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Thanks for your feedback! ❤️")
            return redirect("feedback")
    else:
        form = FeedbackForm()
    return render(request, "home/feedback.html", {"form": form})


def contact_view(request):
    """Handle contact form submissions and send async email notifications."""
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = form.save()

            subject = f"📩 New Contact Message from {contact.name}"
            message = f"""
                You have received a new contact form submission.

                Name: {contact.name}
                Email: {contact.email}
                Message: {contact.message}

                -- Swaadify Contact Form
            """

            send_email_async(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [getattr(settings, 'RESTAURANT_EMAIL', 'admin@example.com')],
                fail_silently=False,
            )

            messages.success(request, "Thank you for contacting us! We’ll get back to you soon.")
            return redirect("contact")
    else:
        form = ContactForm()

    return render(request, "contact.html", {"form": form, "restaurant_name": "Swaadify"})


def custom_404_view(request, exception=None):
    """Custom 404 error handler."""
    return render(request, "404.html", status=404)


# ==========================
# API Views
# ==========================

class MenuCategoryListView(ListAPIView):
    """API endpoint to list all menu categories."""
    queryset = MenuCategory.objects.all().order_by('name')
    serializer_class = MenuCategorySerializer


class MenuItemPagination(PageNumberPagination):
    """Pagination configuration for menu items."""
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class MenuItemViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint to list and search menu items by name."""
    queryset = MenuItem.objects.all().order_by("name")
    serializer_class = MenuItemSerializer
    pagination_class = MenuItemPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ["name"]


class ContactCreateAPIView(generics.CreateAPIView):
    """
    API endpoint to handle contact form submissions.
    Accepts POST requests with name, email, and message.
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
