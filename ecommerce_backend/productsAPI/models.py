from django.db import models
from django.contrib.postgres.fields import ArrayField
import uuid


class Category(models.Model):
    name = models.CharField(max_length=200)
    images = ArrayField(models.CharField(max_length=500), default=list, blank=True)


class Product(models.Model):
    name = models.CharField(max_length=200, default="Not Given")
    details = models.TextField(blank=True)
    price = models.IntegerField()
    images = ArrayField(models.CharField(max_length=500), default=list, blank=True)
    quantity = models.IntegerField()

    rewards = models.IntegerField()
    grant = models.IntegerField()

    coupon_code = models.CharField(max_length=50)
    discount = models.IntegerField()

    tags = ArrayField(models.CharField(max_length=500), default=list)

    product_added_date = models.DateTimeField(auto_now=True)

    # Foreign Keys
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="category"
    )


class FeaturedProduct(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="featured_products"
    )

    SECTIONS = (("home", "home"), ("category", "category"))
    section = models.CharField(max_length=20, choices=SECTIONS)


class OrderedProduct(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="ordered_product"
    )
    quantity = models.IntegerField()
    used_coupon = models.BooleanField(default=False)
    ordered_date = models.DateTimeField(auto_now=True)
    tracking_id = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)


class Wishlist(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="wishlist_product"
    )
    wishlisted_date = models.DateTimeField(auto_now=True)
