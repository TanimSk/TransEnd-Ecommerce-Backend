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
            "name",
            "image_url",
            "price",
        )
        model = FeaturedProduct
