from django.db.models.signals import post_save, post_migrate
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Cart, OrderStatus
from . import DEFAULT_STATUSES
User = get_user_model()

@receiver(post_save, sender=User)
def create_user_cart(sender, instance, created, **kwargs):
    if created:
        Cart.objects.create(user=instance)

@receiver(post_migrate)
def create_default_order_statuses(sender, **kwargs):
    if sender.name == "orders":
        for status in DEFAULT_STATUSES:
            OrderStatus.objects.get_or_create(name=status)
