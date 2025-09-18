from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Cart, CartItem
from products.models import MenuItem

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import Order
from .serializers import OrderSerializer

@login_required
def cart_view(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    return render(request, "cart.html", {"cart": cart})

@login_required
def add_to_cart(request, item_id):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    item = get_object_or_404(MenuItem, id=item_id)
    ci, created = CartItem.objects.get_or_create(cart=cart, menu_item=item)
    if not created:
        ci.quantity += 1
    ci.save()
    return redirect("cart")

@login_required
def update_cart(request, item_id):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    ci = get_object_or_404(CartItem, cart=cart, menu_item_id=item_id)
    if request.method == "POST":
        qty = int(request.POST.get("quantity", 1))
        if qty > 0:
            ci.quantity = qty
            ci.save()
        else:
            ci.delete()
    return redirect("cart")

@login_required
def remove_from_cart(request, item_id):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    ci = get_object_or_404(CartItem, cart=cart, menu_item_id=item_id)
    ci.delete()
    return redirect("cart")



class OrderHistoryAPIView(APIView):
    """
    Authenticated API endpoint to retrieve logged-in user's order history.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        orders = Order.objects.filter(customer=request.user).order_by("-created_at")
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
