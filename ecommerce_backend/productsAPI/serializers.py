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
    image_url = serializers.SerializerMethodField(read_only=True)
    price = serializers.IntegerField(source="product.price_bdt", read_only=True)

    def get_image_url(self, obj):
        first_image = obj.product.images[0]
        if first_image:
            return first_image
        return None

    class Meta:
        fields = (
            "product_id",
            "category_id",
            "name",
            "image_url",
            "price",
        )
        model = FeaturedProduct


class ProductQuerySerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(source="id", read_only=True)
    category_id = serializers.IntegerField(source="category.id", read_only=True)
    image_url = serializers.SerializerMethodField(read_only=True)
    price = serializers.IntegerField(source="price_bdt", read_only=True)

    def get_image_url(self, obj):
        first_image = obj.images[0]
        if first_image:
            return first_image
        return None

    class Meta:
        fields = (
            "product_id",
            "category_id",
            "name",
            "image_url",
            "price",
        )
        model = FeaturedProduct
        model = Product
