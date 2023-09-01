from django.contrib import admin
from .models import Product, Category, FeaturedProduct


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "images")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "images",
        "quantity",
        "rewards",
        "product_added_date",
        "category",
    )

@admin.register(FeaturedProduct)
class FeaturedProductAdmin(admin.ModelAdmin):
    list_display = ("product", "section")
