# Built-in modules
from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib import messages
from django.shortcuts import get_object_or_404

# Django REST Framework modules
from rest_framework import viewsets, generics, status, filters, permissions
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.views import APIView 

# Local modules
from .forms import ContactForm, FeedbackForm
from .models import MenuCategory, Contact
from .serializers import MenuCategorySerializer, MenuItemSerializer, ContactSerializer,TableSerializer,DailySpecialSerializer,UserReviewSerializer,RestaurantSerializer
from .utils import send_email_async
from utils.validation_utils import is_valid_email
from products.models import MenuItem
from .models import Restaurant, Table, UserReview


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

# API Views
class MenuCategoryViewSet(viewsets.ModelViewSet):
    """
    API ViewSet to handle CRUD operations for MenuCategory.
    Supports: list, retrieve, create, update, partial_update, delete.
    """
    queryset = MenuCategory.objects.all().order_by("name")
    serializer_class = MenuCategorySerializer
    lookup_field = "id"

    def create(self, request, *args, **kwargs):
        """Handle category creation with clean response."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(
            {"message": "Menu category created successfully", "data": serializer.data},
            status=status.HTTP_201_CREATED
        )

    def update(self, request, *args, **kwargs):
        """Handle category updates with validation."""
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(
            {"message": "Menu category updated successfully", "data": serializer.data},
            status=status.HTTP_200_OK
        )

    def destroy(self, request, *args, **kwargs):
        """Handle category deletion safely."""
        instance = self.get_object()
        instance.delete()
        return Response({"message": "Menu category deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


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

class AvailableTablesAPIView(generics.ListAPIView):
    """
    API endpoint to list currently available tables.
    Only returns tables where is_available=True.
    """
    queryset = Table.objects.filter(is_available=True).order_by("table_number")
    serializer_class = TableSerializer


class TableListAPIView(generics.ListAPIView):
    """
    API view to list all tables in the restaurant.
    """
    queryset = Table.objects.all().order_by("id")
    serializer_class = TableSerializer


class TableDetailAPIView(generics.RetrieveAPIView):
    """
    API view to retrieve details of a single table by ID.
    """
    queryset = Table.objects.all()
    serializer_class = TableSerializer

    def get(self, request, *args, **kwargs):
        """
        Handles GET request for retrieving a specific table.
        """
        try:
            table = self.get_object()
            serializer = self.get_serializer(table)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Table.DoesNotExist:
            return Response(
                {"detail": "Table not found."},
                status=status.HTTP_404_NOT_FOUND
            )

class DailySpecialsAPIView(generics.ListAPIView):
    """
    API endpoint to list all daily special menu items.
    """
    serializer_class = DailySpecialSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        """
        Return only menu items marked as daily specials.
        """
        return MenuItem.objects.filter(is_daily_special=True).order_by("name")


class UserReviewCreateView(generics.CreateAPIView):
    """
    API endpoint to allow authenticated users to create reviews for menu items.
    """
    serializer_class = UserReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def post(self, request, *args, **kwargs):
        menu_item_id = self.kwargs.get("menu_item_id")
        menu_item = get_object_or_404(MenuItem, id=menu_item_id)

        # Check if the user already reviewed this item
        if UserReview.objects.filter(user=request.user, menu_item=menu_item).exists():
            return Response(
                {"detail": "You have already reviewed this menu item."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user, menu_item=menu_item)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MenuItemReviewListView(generics.ListAPIView):
    """
    API endpoint to retrieve all reviews for a specific menu item.
    """
    serializer_class = UserReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        menu_item_id = self.kwargs.get("menu_item_id")
        return UserReview.objects.filter(menu_item_id=menu_item_id).select_related("user", "menu_item").order_by("-review_date")



class RestaurantInfoView(generics.GenericAPIView):
    """
    API endpoint to retrieve all details about the restaurant.
    GET: Returns restaurant information as JSON.
    """
    serializer_class = RestaurantSerializer

    def get(self, request, *args, **kwargs):
        restaurant = Restaurant.objects.first()  # assuming only one restaurant record
        if not restaurant:
            return Response(
                {"detail": "Restaurant information not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = self.get_serializer(restaurant)
        return Response(serializer.data, status=status.HTTP_200_OK)




class EmailValidationView(APIView):
    """
    Simple API endpoint to validate an email address.
    """

    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response({"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)

        if is_valid_email(email):
            return Response({"message": "Email is valid."}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "Invalid email address."}, status=status.HTTP_400_BAD_REQUEST)
