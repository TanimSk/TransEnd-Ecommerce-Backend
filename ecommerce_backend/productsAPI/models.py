from django.db import models
from django.contrib.postgres.fields import ArrayField
import uuid


class Category(models.Model):
    name = models.CharField(max_length=200)
    images = ArrayField(models.URLField(), default=list, blank=True)

    def __str__(self) -> str:
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=200, default="Not Given")
    details = models.TextField(blank=True)

    price_bdt = models.IntegerField()
    price_usd = models.IntegerField(default=0)
    price_eur = models.IntegerField(default=0)
    price_gbp = models.IntegerField(default=0)
    price_cad = models.IntegerField(default=0)

    images = ArrayField(models.URLField(), default=list, blank=True)
    quantity = models.IntegerField()

    rewards = models.IntegerField()
    grant = models.IntegerField()

    # Discount
    discount_percent = models.IntegerField(default=0)
    discount_bdt = models.IntegerField(default=0)

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
