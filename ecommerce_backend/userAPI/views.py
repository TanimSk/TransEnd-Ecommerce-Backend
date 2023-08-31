from dj_rest_auth.registration.views import RegisterView
from productsAPI.serializers import ProductSerializer
from rest_framework.views import APIView
from rest_framework.response import Response

from productsAPI.models import Product
from .models import Wishlist, OrderedProduct, Consumer
from django.utils import timezone

from rest_framework.permissions import IsAuthenticated
from .serializers import (
    ConsumerCustomRegistrationSerializer,
    WishlistSerializer,
    ProfileSerializer,
    OrderedProductSerializer,
)

# TODO: Add only consumer authentication
# TODO: Update Product Quanity when order is placed


class ConsumerRegistrationView(RegisterView):
    serializer_class = ConsumerCustomRegistrationSerializer


# Add / show Wishlist
class WishlistSerializerAPI(APIView):
    serializer_class = WishlistSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        valid = serializer.is_valid(raise_exception=True)

        if valid:
            product_instance = Product.objects.get(id=serializer.data["product_id"])
            Wishlist(consumer=request.user, product=product_instance).save()
            return Response({"status": "Added to Wishlist"}, status=200)

    def get(self, request, format=None, *args, **kwargs):
        wishlist_products_instance = Product.objects.filter(
            wishlist_product__consumer=request.user
        )
        serialized_products = ProductSerializer(wishlist_products_instance, many=True)
        return Response(serialized_products.data)


# Update / show Profile
class ProfileAPI(APIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None, *args, **kwargs):
        # profile_instance = Consumer.objects.get(consumer=request.user)
        serializer = ProfileSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            profile_instance = Consumer.objects.get(consumer=request.user)
            profile_instance.name = serializer.data.get("name", "")
            profile_instance.phone_number = serializer.data.get("phone_number", "")
            profile_instance.address = serializer.data.get("address", "")
            profile_instance.payment_method = serializer.data.get("payment_method", "")
            profile_instance.inside_dhaka = serializer.data.get("inside_dhaka", "")
            profile_instance.save()

            return Response({"status": "Profile Updated"}, status=200)

    def get(self, request, format=None, *args, **kwargs):
        profile_instance = Consumer.objects.get(consumer=request.user)
        serialized_profile = ProfileSerializer(profile_instance)
        return Response(serialized_profile.data)


# Show / Add Products on Cart, status = "Cart"
class CartAPI(APIView):
    serializer_class = OrderedProductSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None, *args, **kwargs):
        cart_product_instance = OrderedProduct.objects.filter(
            consumer=request.user, status="cart"
        )
        serialized_products = OrderedProductSerializer(cart_product_instance, many=True)
        return Response(serialized_products.data)

    def post(self, request, format=None, *args, **kwargs):
        serializer = OrderedProductSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            product_instance = Product.objects.get(id=serializer.data.get("product_id"))

            if product_instance.quantity < serializer.data.get("ordered_quantity"):
                return Response(
                    {"status": "Quantity cannot be greater than Stock!"}, status=200
                )

            OrderedProduct(
                consumer=request.user,
                product=product_instance,
                ordered_quantity=serializer.data.get("ordered_quantity"),
                status="cart",
            ).save()

            return Response({"status": "Added to Ordered Products"}, status=200)


# add / show Ordered Products, status != "cart"
class OrderProductAPI(APIView):
    # serializer_class = OrderedProductSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, method=None, format=None, *args, **kwargs):
        ordered_product_instance = OrderedProduct.objects.filter(
            consumer=request.user
        ).exclude(status="cart")
        serialized_products = OrderedProductSerializer(
            ordered_product_instance, many=True
        )
        return Response(serialized_products.data)

    # set ordered products
    def post(self, request, method=None, format=None, *args, **kwargs):
        if method == "cod":
            orders_instance = OrderedProduct.objects.filter(
                consumer=request.user, status="cart"
            )
            orders_instance.update(status=method)
            return Response({"status": "Orders Placed!"})

        elif method == "mobile":
            ...
        else:
            return Response({"status": "Invalid Payment Method!"})
