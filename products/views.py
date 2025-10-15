from django.shortcuts import redirect,get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status,permissions

from .models import MenuItem
from .serializers import MenuItemSerializer,MenuItemAvailabilitySerializer
# Create your views here.
class MenuItemView(APIView):
    def get(self, request):
        MenuItems = MenuItem.objects.all()
        serializer = MenuItemSerializer(MenuItems, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = MenuItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def add_to_cart(request, product_id):
    cart = request.session.get('cart', {})

    # Increase quantity if already in cart, else add new
    cart[product_id] = cart.get(product_id, 0) + 1

    # Save back to session
    request.session['cart'] = cart
    request.session.modified = True

    return redirect('home')  # Redirect to homepage or cart page

class MenuItemsByCategoryAPIView(APIView):
    """
    API endpoint to filter menu items by category.
    Example: /api/menu-items/by-category/?category=Pizza
    """

    def get(self, request, *args, **kwargs):
        category_name = request.query_params.get("category")

        if not category_name:
            return Response(
                {"error": "Category parameter is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        menu_items = MenuItem.objects.filter(category__name__iexact=category_name)
        serializer = MenuItemSerializer(menu_items, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
    
class UpdateMenuItemAPIView(APIView):
    """
    API endpoint to update an existing menu item.
    Only admins/staff should be allowed.
    """

    permission_classes = [permissions.IsAdminUser]  # Restrict to admins

    def put(self, request, pk, *args, **kwargs):
        menu_item = get_object_or_404(MenuItem, pk=pk)
        serializer = MenuItemSerializer(menu_item, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MenuItemAvailabilityUpdateView(APIView):
    """
    API endpoint to update the availability status of a MenuItem.
    Example:
        PATCH /api/menu-item/5/availability/
        Body: {"is_available": false}
    """

    def patch(self, request, pk):
        try:
            # Get the menu item by ID
            menu_item = MenuItem.objects.get(pk=pk)
        except MenuItem.DoesNotExist:
            return Response(
                {"error": "Menu item not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Validate request data
        serializer = MenuItemAvailabilitySerializer(menu_item, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": "Menu item availability updated successfully.",
                    "data": serializer.data
                },
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
