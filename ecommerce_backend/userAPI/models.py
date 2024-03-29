from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from productsAPI.models import Product
from django.utils import timezone

# Signals
from django.db.models.signals import post_delete
from django.dispatch import receiver


class User(AbstractUser):
    # Boolean fields to select the type of account.
    is_admin = models.BooleanField(default=False)
    is_consumer = models.BooleanField(default=False)


class Consumer(models.Model):
    consumer = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="consumer"
    )
    name = models.CharField(max_length=200, blank=True)
    phone_number = models.CharField(max_length=100)
    address = models.TextField()
    METHODS = (
        ("cod", "cod"),
        ("mobile", "mobile"),
    )
    payment_method = models.CharField(max_length=50, choices=METHODS, default="mobile")
    inside_dhaka = models.BooleanField(default=False)
    rewards = models.IntegerField(default=0)

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
    ordered_date = models.DateTimeField(blank=True, null=True)
    tracking_id = models.UUIDField(editable=False, blank=True, null=True)

    # Product Specific
    per_price = models.IntegerField(blank=True, null=True)  # Per Product
    total_price = models.IntegerField(blank=True, null=True)
    total_grant = models.IntegerField(blank=True, null=True)
    revenue = models.IntegerField(blank=True, null=True)

    # Global Info
    courier_fee = models.IntegerField(blank=True, null=True)
    order_total_price = models.IntegerField(blank=True, null=True)
    coupon_bdt = models.IntegerField(default=0)
    reward_discount = models.IntegerField(default=0)

    # Global Consumer Info
    consumer_name = models.CharField(max_length=200, blank=True, null=True)
    consumer_phone = models.CharField(max_length=50, blank=True, null=True)
    consumer_email = models.EmailField(max_length=100, blank=True, null=True)
    consumer_address = models.CharField(max_length=500, blank=True, null=True)
    special_instructions = models.CharField(max_length=500, blank=True, null=True)
    METHODS = (
        ("cod", "cod"),
        ("mobile", "mobile"),
    )
    payment_method = models.CharField(max_length=20, choices=METHODS)
    inside_dhaka = models.BooleanField(default=False)

    STATUS = (
        ("cart", "cart"),
        ("paid", "paid"),
        ("cod", "cod"),
        ("delivered", "delivered"),
        ("dispatched", "dispatched"),
    )
    status = models.CharField(max_length=30, choices=STATUS, default="cart")
    dispatched = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"{self.product.name} | {self.consumer.email}"


class Wishlist(models.Model):
    consumer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="wishlist_consumer"
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="wishlist_product"
    )
    wishlisted_date = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.product.name


class OrderPackageTrack(models.Model):
    tracking_id = models.UUIDField(editable=False, unique=True)


# Realtime Count
class AutoDateTimeField(models.DateTimeField):
    def pre_save(self, model_instance, add):
        return timezone.now()


class VisitCount(models.Model):
    user_ref = models.UUIDField()
    last_visit = AutoDateTimeField(default=timezone.now)


@receiver(post_delete, sender=Consumer)
def delete_consumer_user(sender, instance, **kwargs):
    user = instance.consumer
    user.delete()
