from django.contrib import admin
from .models import Product, Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "images")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        # "details",
        "price",
        "images",
        "quantity",
        "rewards",
        # "grant",
        # "coupon_code",
        "discount",
        # "tags",
        "product_added_date",
        "category",
    )
