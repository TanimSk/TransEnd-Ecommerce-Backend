from .models import Product, Category, FeaturedProduct
from rest_framework import serializers


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = Product


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = Category


class FeaturedProductSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(source="product.id", read_only=True)
    category_id = serializers.IntegerField(source="product.category.id", read_only=True)
    name = serializers.CharField(source="product.name", read_only=True)
    image_url = serializers.ListField(source="product.images", read_only=True)
    price = serializers.IntegerField(source="product.price_bdt", read_only=True)

    class Meta:
        fields = (
            "product_id",
            "category_id",
            "name",
            "image_url",
            "price",
        )
        model = FeaturedProduct
