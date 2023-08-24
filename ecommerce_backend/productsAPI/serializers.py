from .models import Product, Category
from rest_framework import serializers


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = Product


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = Category
