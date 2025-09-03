from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import MenuItem
from .serializers import MenuItemSerializer
from django.shortcuts import redirect
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
