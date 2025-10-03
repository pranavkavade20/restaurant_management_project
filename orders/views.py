# Built in models.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from rest_framework.response import Response
from rest_framework import status,permissions

# Local models
from .models import Cart, CartItem,Order
from products.models import MenuItem
from .serializers import OrderSerializer,OrderDetailSerializer
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
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

class OrderViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing customer orders.
    Provides list, retrieve, and custom actions like cancel.
    """
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Customers only see their own orders.
        Staff/Admins can see all orders.
        """
        user = self.request.user
        if user.is_staff:
            return Order.objects.all().order_by("-created_at")
        return Order.objects.filter(customer=user).order_by("-created_at")

    # 🔹 History = just "list" for current user
    @action(detail=False, methods=["get"], url_path="history")
    def history(self, request):
        """
        Retrieve logged-in user's order history.
        Staff gets all orders.
        """
        orders = self.get_queryset()
        serializer = self.get_serializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # 🔹 Cancel order
    @action(detail=True, methods=["delete"], url_path="cancel")
    def cancel_order(self, request, pk=None):
        """
        Cancel an order by setting its status to 'Cancelled'.
        """
        order = get_object_or_404(Order, pk=pk)

        # Permission check: only owner or staff
        if order.customer != request.user and not request.user.is_staff:
            return Response(
                {"detail": "You do not have permission to cancel this order."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Business rules
        if order.order_status == "Cancelled":
            return Response(
                {"detail": "Order is already cancelled."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if order.order_status == "Delivered":
            return Response(
                {"detail": "Delivered orders cannot be cancelled."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Update status
        order.order_status = "Cancelled"
        order.save()

        return Response(
            {"detail": f"Order #{order.id} has been cancelled successfully."},
            status=status.HTTP_200_OK,
        )

