from dj_rest_auth.registration.views import RegisterView
from productsAPI.serializers import ProductSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db import transaction

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
import uuid

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

    """
    POST for adding products in cart
    """

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
            # Check For dublicate products
            if OrderedProduct.objects.filter(
                dispatched=False, product_id=serializer.data.get("product_id")
            ).exists():
                return Response({"status": "This Product Already exists in your cart!"})

            # Add to Cart
            product_instance = Product.objects.get(id=serializer.data.get("product_id"))
            if product_instance.quantity < serializer.data.get("ordered_quantity"):
                return Response(
                    {"status": "Quantity cannot be greater than Stock!"}, status=200
                )

            OrderedProduct(
                consumer=request.user,
                product=product_instance,
                ordered_quantity=serializer.data.get("ordered_quantity"),
                # ordered_date=timezone.now(),
                status="cart",
            ).save()

            return Response({"status": "Added to Ordered Products"}, status=200)


# add / show Ordered Products, status != "cart"
class OrderProductAPI(APIView):

    """
    POST for moving products from cart to ordered_products
    """

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

    # Set ordered products
    def post(self, request, method=None, format=None, *args, **kwargs):
        orders_instance = OrderedProduct.objects.filter(
            consumer=request.user, status="cart"
        )
        consumer_instance = Consumer.objects.get(consumer=request.user)

        if orders_instance.count() == 0:
            return Response({"status": "No products in cart!"})

        if method == "cod":
            orders_instance.update(
                status=method, ordered_date=timezone.now(), tracking_id=uuid.uuid4()
            )

            # Update Product Quantity & Quantity Sold, increase Rewards
            with transaction.atomic():
                for order_instance in orders_instance:
                    product_instance = Product.objects.get(
                        ordered_product=order_instance
                    )
                    product_instance.quantity -= order_instance.ordered_quantity
                    product_instance.quantity_sold += order_instance.ordered_quantity

                    # Updating Rewards (Increment)
                    consumer_instance.rewards += (
                        product_instance.rewards * order_instance.ordered_quantity
                    )

                    # Update bought price in orders
                    discount = (
                        product_instance.discount_percent
                        * product_instance.price_bdt
                        / 100
                    )
                    if discount > product_instance.discount_max_bdt:
                        discount = product_instance.discount_max_bdt
                    order_instance.price_bought = product_instance.price_bdt - discount

                    product_instance.save()
                    order_instance.save()
                    consumer_instance.save()

            return Response({"status": "Orders Placed!"})

        elif method == "mobile":
            ...

        else:
            return Response({"status": "Invalid Payment Method!"})
