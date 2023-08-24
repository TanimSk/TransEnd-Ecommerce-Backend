from django.shortcuts import render

from .serializers import ProductSerializer, CategorySerializer
from .models import Category, Product

from rest_framework.views import APIView
from rest_framework.response import Response


class CategoryAPI(APIView):
    """
    Categories and Products
    """

    def get(
        self, request, category_id=None, product_id=None, format=None, *args, **kwargs
    ):
        # Return Categories
        if category_id is None:
            categories = Category.objects.all()
            serialized_categories = CategorySerializer(categories, many=True)
            return Response(serialized_categories.data)

        # Return Category Specific Products
        elif product_id is None:
            products = Product.objects.filter(category_id=category_id)
            serialized_products = ProductSerializer(products, many=True)
            return Response(serialized_products.data)

        # Return Specific Product
        else:
            try:
                product = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                product = None
            serialized_product = ProductSerializer(product)
            return Response(serialized_product.data)
