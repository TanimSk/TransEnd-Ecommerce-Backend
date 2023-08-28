from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from productsAPI.models import Product

# Signals
from django.db.models.signals import post_delete
from django.dispatch import receiver
import uuid


class User(AbstractUser):
    # Boolean fields to select the type of account.
    is_admin = models.BooleanField(default=False)
    is_consumer = models.BooleanField(default=False)


class Consumer(models.Model):
    consumer = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="consumer"
    )
    name = models.CharField(max_length=200, blank=True)
    phone_number = models.BigIntegerField()
    address = models.TextField()
    METHODS = (
        ("cod", "cod"),
        ("mobile", "mobile"),
    )
    payment_method = models.CharField(max_length=50, choices=METHODS)
    inside_dhaka = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.consumer.email


# Order and wishlist
class OrderedProduct(models.Model):
    consumer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="order_consumer"
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="ordered_product"
    )
    ordered_quantity = models.IntegerField()
    used_coupon = models.BooleanField(default=False)
    ordered_date = models.DateTimeField(auto_now=True)
    tracking_id = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)

    STATUS = (
        ("paid", "paid"),
        ("unpaid", "unpaid"),
        ("delivered", "delivered"),
    )
    status = models.CharField(max_length=30, choices=STATUS, default="unpaid")
    dispatched = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"{self.product.name} | {self.consumer.email}"


class Wishlist(models.Model):
    consumer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="wishlist_consumer"
    )
    product = models.OneToOneField(
        Product, on_delete=models.CASCADE, related_name="wishlist_product"
    )
    wishlisted_date = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.product.name


@receiver(post_delete, sender=Consumer)
def delete_consumer_user(sender, instance, **kwargs):
    user = instance.consumer
    user.delete()
