from django.db import models
from django.contrib.postgres.fields import ArrayField
from vendorAPI.models import Vendor

# Signals
# from django.db.models.signals import post_delete
# from django.dispatch import receiver


class Category(models.Model):
    name = models.CharField(max_length=200)
    images = ArrayField(models.URLField(), default=list, blank=True)

    def __str__(self) -> str:
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=200)
    details = models.TextField(blank=True)
    tags = ArrayField(models.CharField(max_length=500), default=list, blank=True)

    # Price
    price_bdt = models.IntegerField()
    price_usd = models.FloatField(default=0)
    price_gbp = models.FloatField(default=0)
    price_eur = models.FloatField(default=0)
    price_cad = models.FloatField(default=0)

    images = ArrayField(models.URLField(), default=list, blank=True)
    quantity = models.IntegerField()

    rewards = models.IntegerField(default=0)
    grant = models.IntegerField(default=0)

    # Discount
    discount_percent = models.IntegerField(default=0)
    discount_max_bdt = models.IntegerField(default=0)

    # Product Trace
    product_added_date = models.DateTimeField(auto_now=True)
    quantity_sold = models.IntegerField(default=0)

    # Foreign Keys
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="category"
    )
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name="vendor")

    def __str__(self) -> str:
        return self.name


class FeaturedProduct(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="featured_products"
    )

    SECTIONS = (("home", "home"), ("category", "category"))
    section = models.CharField(max_length=20, choices=SECTIONS)

    def __str__(self) -> str:
        return self.product.name
