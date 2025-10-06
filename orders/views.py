# ==========================
# Built-in & Third-Party Imports
# ==========================
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

# ==========================
# Local Imports
# ==========================
from .models import Cart, CartItem, Order, Coupon
from products.models import MenuItem
from .serializers import OrderSerializer


# ==========================
# Web Views (Cart Operations)
# ==========================

@login_required
def cart_view(request):
    """Display the user's shopping cart."""
    cart, _ = Cart.objects.get_or_create(user=request.user)
    return render(request, "cart.html", {"cart": cart})


@login_required
def add_to_cart(request, item_id):
    """Add a menu item to the user's cart."""
    cart, _ = Cart.objects.get_or_create(user=request.user)
    item = get_object_or_404(MenuItem, id=item_id)

    cart_item, created = CartItem.objects.get_or_create(cart=cart, menu_item=item)
    if not created:
        cart_item.quantity += 1
    cart_item.save()

    return redirect("cart")


@login_required
def update_cart(request, item_id):
    """Update the quantity of a cart item or remove it if quantity is zero."""
    cart, _ = Cart.objects.get_or_create(user=request.user)
    cart_item = get_object_or_404(CartItem, cart=cart, menu_item_id=item_id)

    if request.method == "POST":
        try:
            qty = int(request.POST.get("quantity", 1))
        except ValueError:
            qty = 1

        if qty > 0:
            cart_item.quantity = qty
            cart_item.save()
        else:
            cart_item.delete()

    return redirect("cart")


@login_required
def remove_from_cart(request, item_id):
    """Remove an item from the user's cart."""
    cart, _ = Cart.objects.get_or_create(user=request.user)
    cart_item = get_object_or_404(CartItem, cart=cart, menu_item_id=item_id)
    cart_item.delete()
    return redirect("cart")


# ==========================
# API Views (Orders & Coupons)
# ==========================

class OrderViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing customer orders.
    Provides list, retrieve, create, and cancel functionality.
    """
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Customers see only their own orders.
        Staff/Admins see all orders.
        """
        user = self.request.user
        return (
            Order.objects.all().order_by("-created_at")
            if user.is_staff
            else Order.objects.filter(customer=user).order_by("-created_at")
        )

    @action(detail=False, methods=["get"], url_path="history")
    def history(self, request):
        """Return the logged-in user's order history."""
        orders = self.get_queryset()
        serializer = self.get_serializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["delete"], url_path="cancel")
    def cancel_order(self, request, pk=None):
        """
        Cancel an order by setting its status to 'Cancelled'.
        Only the owner or staff can perform this action.
        """
        order = get_object_or_404(Order, pk=pk)

        # Authorization check
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

        # Perform cancellation
        order.order_status = "Cancelled"
        order.save(update_fields=["order_status"])

        return Response(
            {"detail": f"Order #{order.id} has been cancelled successfully."},
            status=status.HTTP_200_OK,
        )


class CouponValidationView(APIView):
    """
    API endpoint to validate a coupon code.
    Returns coupon details if valid, with proper error handling.
    """

    def post(self, request, *args, **kwargs):
        code = request.data.get("code", "").strip()

        if not code:
            return Response(
                {"detail": "Coupon code is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        coupon = Coupon.objects.filter(code__iexact=code).first()
        if not coupon:
            return Response(
                {"detail": "Invalid coupon code."},
                status=status.HTTP_404_NOT_FOUND,
            )

        now = timezone.now()

        # Validation checks
        if not coupon.is_active:
            return Response(
                {"detail": "This coupon is no longer active."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if coupon.valid_from and coupon.valid_from > now:
            return Response(
                {"detail": "This coupon is not yet valid."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if coupon.valid_to and coupon.valid_to < now:
            return Response(
                {"detail": "This coupon has expired."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Valid coupon
        return Response(
            {
                "success": True,
                "message": "Coupon is valid.",
                "data": {
                    "code": coupon.code,
                    "discount": float(coupon.discount),
                    "valid_from": coupon.valid_from,
                    "valid_to": coupon.valid_to,
                },
            },
            status=status.HTTP_200_OK,
        )
