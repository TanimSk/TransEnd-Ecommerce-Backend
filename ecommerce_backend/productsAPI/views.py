from rest_framework import generics
from rest_framework import filters

from .serializers import (
    ProductSerializer,
    CategorySerializer,
    FeaturedProductSerializer,
    ProductQuerySerializer
)
from .models import Category, Product, FeaturedProduct
from userAPI.models import Wishlist
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination


# Pagination Config
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = "page_size"
    max_page_size = 10
    page_query_param = "p"


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
            products = Product.objects.filter(category_id=category_id, quantity__gt=0)
            paginator = StandardResultsSetPagination()
            result_page = paginator.paginate_queryset(products, request)
            serializer = ProductSerializer(result_page, many=True)
            return paginator.get_paginated_response(serializer.data)

        # Return Specific Product
        else:
            try:
                product = Product.objects.get(id=product_id)
                serialized_product = ProductSerializer(product)

                print(request.user.is_authenticated)

                if request.user.is_authenticated:
                    wishlisted = Wishlist.objects.filter(consumer=request.user, product=product).exists()
                    return Response({**serialized_product.data, "wishlisted": wishlisted})

                return Response(serialized_product.data)
            
            except Product.DoesNotExist:
                return Response({"status": "No Products Found!"})

            


class FilterAPI(APIView):
    """
    Filter Category Specific Products

    params are: low_to_high, high_to_low, best_sold, new_arrival
    For pagination:  ?p=1&page_size=3
    """

    def get(self, request, category_id, param, format=None, *args, **kwargs):
        product_instance = None

        if param == "low_to_high":
            product_instance = Product.objects.filter(
                category_id=category_id, quantity__gt=0
            ).order_by("price_bdt")

        elif param == "high_to_low":
            product_instance = Product.objects.filter(
                category_id=category_id, quantity__gt=0
            ).order_by("-price_bdt")

        elif param == "best_sold":
            product_instance = Product.objects.filter(
                category_id=category_id, quantity__gt=0
            ).order_by("-quantity_sold")

        elif param == "new_arrival":
            product_instance = Product.objects.filter(
                category_id=category_id, quantity__gt=0
            ).order_by("-product_added_date")

        if product_instance is not None:
            paginator = StandardResultsSetPagination()
            result_page = paginator.paginate_queryset(product_instance, request)
            serializer = ProductSerializer(result_page, many=True)
            return paginator.get_paginated_response(serializer.data)

        return Response({"status": "Invalid Filtering Parameters!"})


# Search API
class SearchAPI(generics.ListCreateAPIView):
    http_method_names = ["get"]
    search_fields = [
        "name",
        "details",
        "tags",
    ]
    filter_backends = (filters.SearchFilter,)
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    pagination_class = StandardResultsSetPagination


# Featured Products API
class FeaturedProductAPI(APIView):
    serializer_class = FeaturedProductSerializer

    def get(self, request, section, format=None, *args, **kwargs):
        if section == "home" or section == "category":
            products_instance = FeaturedProduct.objects.filter(section=section)
            serialized_products = self.serializer_class(products_instance, many=True)
            return Response(serialized_products.data)

        return Response({"status": "wrong routing!"}, status=404)
