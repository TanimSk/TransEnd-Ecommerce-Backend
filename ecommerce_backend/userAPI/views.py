from dj_rest_auth.registration.views import RegisterView
from productsAPI.serializers import ProductSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db import transaction
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from productsAPI.models import Product
from .models import Wishlist, OrderedProduct, Consumer
from adminAPI.models import ExtraPayment
from django.utils import timezone

from rest_framework.permissions import BasePermission
from .serializers import (
    ConsumerCustomRegistrationSerializer,
    # WishlistSerializer,
    ProfileSerializer,
    OrderedProductSerializer,
)
from .utils import make_payment, verify_payment, send_invoice
import uuid


# ------------------------------------------------------------------------------------
# Update Product Quantity & Quantity Sold, increase Rewards, Total Price, Total Grant
# ------------------------------------------------------------------------------------
def update_order(method, orders_instance, consumer_instance):
    order_total_price = 0
    courier_fee = 0

    context = {
        "customer_name": consumer_instance.name,
        "email": consumer_instance.consumer.email,
        "address": consumer_instance.address,
        "phone_number": consumer_instance.phone_number,
        "orders_info": [],
    }

    with transaction.atomic():
        for order_instance in orders_instance:
            product_instance = Product.objects.get(ordered_product=order_instance)
            product_instance.quantity -= order_instance.ordered_quantity
            product_instance.quantity_sold += order_instance.ordered_quantity

            # Updating Rewards (Increment)
            consumer_instance.rewards += (
                product_instance.rewards * order_instance.ordered_quantity
            )

            # Update bought_price, total_grant & total_price in orders
            discount = (
                product_instance.discount_percent * product_instance.price_bdt / 100
            )

            if (
                product_instance.discount_max_bdt != 0
                and discount > product_instance.discount_max_bdt
            ):
                discount = product_instance.discount_max_bdt

            # Calculations
            per_price = product_instance.price_bdt - discount
            total_price = per_price * order_instance.ordered_quantity
            total_grant = product_instance.grant * order_instance.ordered_quantity
            revenue = total_price - total_grant

            # Setting the Values
            order_instance.per_price = per_price
            order_instance.total_price = total_price
            order_instance.total_grant = total_grant
            order_instance.revenue = revenue
            order_total_price += total_price

            # Adding Courier Charges
            extra_payment_instance = ExtraPayment.objects.first()
            if consumer_instance.inside_dhaka:
                order_instance.courier_fee = extra_payment_instance.inside_dhaka
                courier_fee = extra_payment_instance.inside_dhaka
            else:
                order_instance.courier_fee = extra_payment_instance.outside_dhaka
                courier_fee = extra_payment_instance.outside_dhaka

            # Adding Order Info
            context["orders_info"].append(
                {
                    "product_name": product_instance.name,
                    "quantity": order_instance.ordered_quantity,
                    "price": total_price,
                }
            )

            product_instance.save()
            order_instance.save()
            consumer_instance.save()

    order_total_price += courier_fee
    order_id = uuid.uuid4()

    # Adding order Info
    context["order_id"] = order_id
    context["courier_fee"] = courier_fee
    context["total_price"] = order_total_price

    orders_instance.update(
        status=method,
        ordered_date=timezone.now(),
        tracking_id=order_id,
        order_total_price=order_total_price,
    )

    return context


# ----------------
# GET TOTAL PRICE
# ----------------
def get_price(orders_instance, user):
    if orders_instance.count() == 0:
        return Response({"status": "No products in cart!"})

    consumer_instance = Consumer.objects.get(consumer=user)

    to_be_paid = 0
    total_grant = 0
    courier_fee = 0

    for order_instance in orders_instance:
        product_instance = Product.objects.get(ordered_product=order_instance)

        # get bought_price, total_grant & total_price in orders
        discount = product_instance.discount_percent * product_instance.price_bdt / 100

        if (
            product_instance.discount_max_bdt != 0
            and discount > product_instance.discount_max_bdt
        ):
            discount = product_instance.discount_max_bdt

        # Calculations
        per_price = product_instance.price_bdt - discount
        total_price = per_price * order_instance.ordered_quantity
        to_be_paid += total_price
        total_grant += product_instance.grant * order_instance.ordered_quantity

    # Extra fees
    extra_payment_instance = ExtraPayment.objects.first()
    if consumer_instance.inside_dhaka:
        to_be_paid += extra_payment_instance.inside_dhaka
        courier_fee = extra_payment_instance.inside_dhaka
    else:
        to_be_paid += extra_payment_instance.outside_dhaka
        courier_fee = extra_payment_instance.outside_dhaka

    return {
        "total_price": to_be_paid,
        "total_grant": total_grant,
        "courier_fee": courier_fee,
    }


# Authenticate User Only Class
class AuthenticateOnlyConsumer(BasePermission):
    def has_permission(self, request, view):
        if request.user and request.user.is_authenticated:
            if request.user.is_consumer:
                return True
            else:
                return False
        return False


class ConsumerRegistrationView(RegisterView):
    serializer_class = ConsumerCustomRegistrationSerializer


# Add / show Wishlist
class WishlistSerializerAPI(APIView):

    """
    Wishlisted Products can be viewed & removed.
    Pass product_id as a param for removing and adding
    """

    permission_classes = [AuthenticateOnlyConsumer]

    def post(self, request, product_id=None, format=None, *args, **kwargs):
        if product_id is None:
            return Response({"status": "param missing"})

        product_instance = Product.objects.get(id=product_id)

        if not Wishlist.objects.filter(
            consumer=request.user, product=product_instance
        ).exists():
            Wishlist(consumer=request.user, product=product_instance).save()
            return Response({"status": "Added To Wishlist"})

        return Response({"status": "Product Already Exits in Wishlist!"})

    def get(self, request, format=None, *args, **kwargs):
        wishlist_products_instance = Product.objects.filter(
            wishlist_product__consumer=request.user
        )
        serialized_products = ProductSerializer(wishlist_products_instance, many=True)
        return Response(serialized_products.data)

    def delete(self, request, product_id=None, format=None, *args, **kwargs):
        if product_id is None:
            return Response({"status": "param missing"})

        product_instance = Product.objects.get(id=product_id)
        Wishlist.objects.filter(
            consumer=request.user, product=product_instance
        ).first().delete()
        return Response({"status": "Removed From Wishlist"})


# Update / show Profile
class ProfileAPI(APIView):
    serializer_class = ProfileSerializer
    permission_classes = [AuthenticateOnlyConsumer]

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
    POST for adding products in cart.
    For deleting a product add a param <product_id>
    """

    serializer_class = OrderedProductSerializer
    permission_classes = [AuthenticateOnlyConsumer]

    def get(self, request, format=None, *args, **kwargs):
        cart_product_instance = OrderedProduct.objects.filter(
            consumer=request.user, status="cart"
        )

        if not cart_product_instance.exists():
            return Response({"status": "Cart is Empty!"})

        serialized_products = OrderedProductSerializer(cart_product_instance, many=True)
        return Response(
            {
                "products": serialized_products.data,
                **get_price(cart_product_instance, request.user),
            }
        )

    def post(self, request, format=None, *args, **kwargs):
        serializer = OrderedProductSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            # Check For dublicate products
            if OrderedProduct.objects.filter(
                consumer=request.user,
                status="cart",
                product_id=serializer.data.get("product_id"),
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
                status="cart",
            ).save()

            return Response({"status": "Added to Cart"}, status=200)

    def delete(self, request, product_id=None, format=None, *args, **kwargs):
        if product_id is None:
            return Response({"status": "Params Required!"})

        OrderedProduct.objects.get(
            consumer=request.user, product_id=product_id, status="cart"
        ).delete()
        return Response({"status": "Removed Product From Cart"})


# add / show Ordered Products, status != "cart"
class OrderProductAPI(APIView):

    """
    For Ordering, POST with <method> param.
    GET request, to see order history
    """

    permission_classes = [AuthenticateOnlyConsumer]

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
            # Update Product Quantity & Quantity Sold, increase Rewards, Total Price, Total Grant
            context = update_order(method, orders_instance, consumer_instance)
            send_invoice(consumer_instance.consumer.email, context)
            return Response({"status": "Orders Placed!"})

        elif method == "mobile":
            if verify_payment(request.GET.get("uuid")):
                update_order(method, orders_instance, consumer_instance)
                send_invoice(consumer_instance.consumer.email, context)
                return render(request, "payment_success.html")

        else:
            return Response({"status": "Invalid Payment Method!"})


# COD Order
class OrderProductCODAPI(APIView):
    permission_classes = [AuthenticateOnlyConsumer]

    # Set ordered products
    def post(self, request, format=None, *args, **kwargs):
        orders_instance = OrderedProduct.objects.filter(
            consumer=request.user, status="cart"
        )
        consumer_instance = Consumer.objects.get(consumer=request.user)

        if orders_instance.count() == 0:
            return Response({"status": "No products in cart!"})

        # Update Product Quantity & Quantity Sold, increase Rewards, Total Price, Total Grant
        context = update_order("cod", orders_instance, consumer_instance)
        send_invoice(consumer_instance.consumer.email, context)
        return Response({"status": "Orders Placed!"})


# Mobile Order
@csrf_exempt
def OrderProductMobileAPI(request):
    # Set ordered products
    if request.method == "POST":
        orders_instance = OrderedProduct.objects.filter(
            consumer=request.user, status="cart"
        )
        consumer_instance = Consumer.objects.get(consumer=request.user)

        if orders_instance.count() == 0:
            return Response({"status": "No products in cart!"})

        if verify_payment(request.GET.get("uuid")):
            context = update_order("mobile", orders_instance, consumer_instance)
            send_invoice(consumer_instance.consumer.email, context)
            return render(request, "payment_success.html")


# Make Payment
class PaymentLinkAPI(APIView):
    """
    Send post request for getting the gateway link
    """

    permission_classes = [AuthenticateOnlyConsumer]

    def post(self, request, method=None, format=None, *args, **kwargs):
        consumer_instance = Consumer.objects.get(consumer=request.user)

        # ------- Calculating Total Price ---------
        orders_instance = OrderedProduct.objects.filter(
            consumer=request.user, status="cart"
        )
        if orders_instance.count() == 0:
            return Response({"status": "No products in cart!"})

        to_be_paid = get_price(orders_instance, request.user)["total_price"]

        response = make_payment(
            cus_name=consumer_instance.name,
            cus_email=consumer_instance.consumer.email,
            cus_phone=consumer_instance.phone_number,
            amount=to_be_paid,
        )

        return Response(response)
