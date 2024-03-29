from dj_rest_auth.registration.views import RegisterView
from productsAPI.serializers import ProductSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db import transaction
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from productsAPI.models import Product
from .models import Wishlist, OrderedProduct, Consumer, OrderPackageTrack, VisitCount
from adminAPI.models import ExtraPayment, CouponCode, Reward
from django.utils import timezone
from rest_framework.permissions import BasePermission
from .serializers import (
    ConsumerCustomRegistrationSerializer,
    WishlistSerializer,
    PlaceOrderSerializer,
    ProfileSerializer,
    OrderedProductSerializer,
    CouponSerializer,
    VisitCountSerializer,
)
from django.db.models import Count
from dj_rest_auth.registration.views import SocialConnectView
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView
from .utils import make_payment, verify_payment, send_invoice
import uuid


# ------------------------------------------------------------------------------------
# Update Product Quantity & Quantity Sold, increase Rewards, Total Price, Total Grant
# ------------------------------------------------------------------------------------
def update_order(method, orders_instance, consumer_instance):
    order_total_price = 0
    courier_fee = 0
    coupon_discount = 0
    reward_discount = 0
    order_id = uuid.uuid4()

    context = {
        "customer_name": orders_instance[0].consumer_name,
        "email": orders_instance[0].consumer_email,
        "address": orders_instance[0].consumer_address,
        "phone_number": orders_instance[0].consumer_phone,
        "orders_info": [],
    }

    if orders_instance.filter(reward_discount__gt=0).exists():
        consumer_instance.rewards = 0

    with transaction.atomic():
        for order_instance in orders_instance:
            product_instance = Product.objects.get(ordered_product=order_instance)
            product_instance.quantity -= order_instance.ordered_quantity
            product_instance.quantity_sold += order_instance.ordered_quantity

            # coupon_discount & reward_discount
            if order_instance.coupon_bdt > 0:
                coupon_discount = order_instance.coupon_bdt
            if order_instance.reward_discount > 0:
                reward_discount = order_instance.reward_discount

            # Updating Rewards (Increment & Decrement)
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

    # Adding Courier Charges
    extra_payment_instance = ExtraPayment.objects.first()
    if orders_instance[0].inside_dhaka:
        courier_fee = extra_payment_instance.inside_dhaka
    else:
        courier_fee = extra_payment_instance.outside_dhaka

    # Total Price
    order_total_price += courier_fee
    order_total_price -= coupon_discount
    order_total_price -= reward_discount

    # Adding order Info
    context["order_id"] = order_id
    context["courier_fee"] = courier_fee
    context["total_price"] = order_total_price
    context["reward_discount"] = reward_discount
    context["coupon_discount"] = coupon_discount

    orders_instance.update(
        courier_fee=courier_fee,
        status=method if method == "cod" else "paid",
        ordered_date=timezone.now(),
        tracking_id=order_id,
        order_total_price=order_total_price,
    )

    OrderPackageTrack.objects.create(tracking_id=order_id)

    return context


# -----------------
# GET TOTAL PRICE
# -----------------
def get_price(orders_instance, inside_dhaka):
    if orders_instance.count() == 0:
        return False

    # consumer_instance = Consumer.objects.get(consumer=user)

    to_be_paid = 0
    total_grant = 0
    courier_fee = 0
    coupon_discount = 0
    reward_discount = 0

    for order_instance in orders_instance:
        product_instance = Product.objects.get(ordered_product=order_instance)

        # get bought_price, total_grant & total_price in orders
        discount = product_instance.discount_percent * product_instance.price_bdt / 100

        # Do not overwrite with 0 value
        if order_instance.coupon_bdt > 0:
            coupon_discount = order_instance.coupon_bdt
        if order_instance.reward_discount > 0:
            reward_discount = order_instance.reward_discount

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
    if inside_dhaka is None:
        courier_fee = None
    elif inside_dhaka:
        to_be_paid += extra_payment_instance.inside_dhaka
        courier_fee = extra_payment_instance.inside_dhaka
    else:
        to_be_paid += extra_payment_instance.outside_dhaka
        courier_fee = extra_payment_instance.outside_dhaka

    raw_price = to_be_paid

    # Reduce Price
    to_be_paid -= coupon_discount
    to_be_paid -= reward_discount

    return {
        "reward_discount": reward_discount,
        "coupon_discount": coupon_discount,
        "raw_price": raw_price,
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
            return Response({"error": "param missing"})

        product_instance = Product.objects.get(id=product_id)

        if not Wishlist.objects.filter(
            consumer=request.user, product=product_instance
        ).exists():
            Wishlist.objects.create(consumer=request.user, product=product_instance)
            return Response({"status": "Added To Wishlist"})

        return Response({"error": "Product Already Exits in Wishlist!"})

    def get(self, request, format=None, *args, **kwargs):
        wishlist_products_instance = Wishlist.objects.filter(consumer=request.user)
        serialized_products = WishlistSerializer(wishlist_products_instance, many=True)
        return Response(serialized_products.data)

    def delete(self, request, product_id=None, format=None, *args, **kwargs):
        if product_id is None:
            return Response({"error": "param missing"})

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
        ).order_by("product__name")

        if not cart_product_instance.exists():
            return Response({"status": "Cart is Empty!"})

        serialized_products = OrderedProductSerializer(cart_product_instance, many=True)
        extra_payment_instance = ExtraPayment.objects.first()
        return Response(
            {
                "products": serialized_products.data,
                **get_price(cart_product_instance, None),
                "inside_dhaka": extra_payment_instance.inside_dhaka,
                "outside_dhaka": extra_payment_instance.outside_dhaka,
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
                return Response({"error": "This Product Already Exists In Your Cart!"})

            # Add to Cart
            product_instance = Product.objects.get(id=serializer.data.get("product_id"))
            if product_instance.quantity < serializer.data.get("ordered_quantity"):
                return Response(
                    {"error": "Quantity Cannot Be Greater Than Stock!"}, status=200
                )

            OrderedProduct(
                consumer=request.user,
                product=product_instance,
                ordered_quantity=serializer.data.get("ordered_quantity"),
                status="cart",
            ).save()

            return Response({"status": "Added To Cart"}, status=200)

    def put(self, request, format=None, *args, **kwargs):
        serializer = OrderedProductSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            # Get Product
            order_product_instance = OrderedProduct.objects.get(
                consumer=request.user,
                product_id=serializer.data.get("product_id"),
                status="cart",
            )

            # Quantity Check
            product_instance = Product.objects.get(id=serializer.data.get("product_id"))
            if product_instance.quantity < serializer.data.get("ordered_quantity"):
                return Response(
                    {"error": "Quantity Cannot Be Greater Than Stock!"}, status=200
                )

            order_product_instance.ordered_quantity = serializer.data.get(
                "ordered_quantity"
            )
            order_product_instance.save()

            return Response({"status": "Quantity Updated"}, status=200)

    def delete(self, request, product_id=None, format=None, *args, **kwargs):
        if product_id is None:
            return Response({"error": "Params Required!"})

        OrderedProduct.objects.get(
            consumer=request.user, product_id=product_id, status="cart"
        ).delete()
        return Response({"status": "Removed Product From Cart"})


class CartCountAPI(APIView):
    serializer_class = OrderedProductSerializer
    permission_classes = [AuthenticateOnlyConsumer]

    def get(self, request, method=None, format=None, *args, **kwargs):
        ordered_instance = OrderedProduct.objects.filter(
            consumer=request.user, status="cart"
        )
        return Response({"cart_count": ordered_instance.count()})


# add / show Ordered Products, status != "cart"
class OrderProductAPI(APIView):

    """
    For Ordering, POST with <method> param.
    GET request, to see order history
    """

    permission_classes = [AuthenticateOnlyConsumer]

    def get(self, request, method=None, format=None, *args, **kwargs):
        response_arr = []

        order_traces = (
            OrderedProduct.objects.filter(consumer=request.user)
            .exclude(status="cart")
            .values("tracking_id")
            .annotate(Count("tracking_id"))
        )

        for order_trace in order_traces:
            ordered_product_instances = OrderedProduct.objects.filter(
                tracking_id=order_trace["tracking_id"]
            )
            serialized_products = OrderedProductSerializer(
                ordered_product_instances, many=True
            )
            response_arr.append(
                {
                    "info": {
                        "ordered_date": serialized_products.data[0]["ordered_date"],
                        "status": serialized_products.data[0]["status"],
                        "coupon": serialized_products.data[0]["coupon_bdt"],
                        "reward": serialized_products.data[0]["reward_discount"],
                        "total_price": serialized_products.data[0]["order_total_price"],
                        "address": serialized_products.data[0]["consumer_address"],
                        "inside_dhaka": serialized_products.data[0]["inside_dhaka"],
                    },
                    "products": serialized_products.data,
                }
            )

        return Response(response_arr)


# COD Order
class OrderProductCODAPI(APIView):
    permission_classes = [AuthenticateOnlyConsumer]
    serializer_class = PlaceOrderSerializer

    # Set ordered products
    def post(self, request, format=None, *args, **kwargs):
        serializer = PlaceOrderSerializer(data=request.data)

        if not serializer.is_valid(raise_exception=True):
            return Response({"error": "An Error Occured"})

        orders_instance = OrderedProduct.objects.filter(
            consumer=request.user, status="cart"
        )
        consumer_instance = Consumer.objects.get(consumer=request.user)

        if orders_instance.count() == 0:
            return Response({"error": "No Products In Cart!"})

        # Save User Global Info to Ordered Object
        orders_instance.update(**serializer.data)

        # Update Product Quantity & Quantity Sold, increase Rewards, Total Price, Total Grant
        context = update_order("cod", orders_instance, consumer_instance)
        send_invoice(consumer_instance.consumer.email, context)

        return Response({"status": "Orders Placed!"})


# Mobile Order (will be redirecting via aamarPay)
@csrf_exempt
def OrderProductMobileAPI(request):
    # Set ordered products
    if request.method == "POST":
        orders_instance = OrderedProduct.objects.filter(
            consumer__email=request.GET.get("email"), status="cart"
        )
        consumer_instance = Consumer.objects.get(
            consumer__email=request.GET.get("email")
        )

        if orders_instance.count() == 0:
            return Response({"status": "No Products In Cart!"})

        if verify_payment(request.GET.get("uuid")):
            context = update_order("mobile", orders_instance, consumer_instance)
            send_invoice(consumer_instance.consumer.email, context)
            return render(request, "payment_success.html")


# Make Mobile Payment
class PaymentLinkAPI(APIView):
    """
    Send post request for getting the gateway link
    """

    permission_classes = [AuthenticateOnlyConsumer]
    serializer_class = PlaceOrderSerializer

    def post(self, request, method=None, format=None, *args, **kwargs):
        serializer = PlaceOrderSerializer(data=request.data)

        if not serializer.is_valid(raise_exception=True):
            return Response({"error": "An Error Occured"})

        consumer_instance = Consumer.objects.get(consumer=request.user)

        # ------- Calculating Total Price ---------
        orders_instance = OrderedProduct.objects.filter(
            consumer=request.user, status="cart"
        )
        if orders_instance.count() == 0:
            return Response({"error": "No Products In Cart!"})

        to_be_paid = get_price(orders_instance, serializer.data.get("inside_dhaka"))[
            "total_price"
        ]

        response = make_payment(
            cus_name=consumer_instance.name,
            cus_email=consumer_instance.consumer.email,
            cus_phone=serializer.data.get("consumer_phone"),
            amount=to_be_paid,
        )

        # Save User Global Info to Ordered Object
        orders_instance.update(**serializer.data)

        return Response(response)


class UseCouponAPI(APIView):
    """
    POST - update order model.
    """

    permission_classes = [AuthenticateOnlyConsumer]
    serializer_class = CouponSerializer

    def post(self, request, format=None, *args, **kwargs):
        serializer = CouponSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            coupon_code = serializer.data.get("coupon_code")

            if coupon_code is None:
                return Response({"error": "Coupon Code Missing!"})

            # Verify Coupon
            coupon_instance = (
                CouponCode.objects.filter(code=coupon_code)
                .order_by("-coupon_added")
                .first()
            )

            if coupon_instance is None:
                return Response({"error": "Invalid Coupon!"})

            if (
                coupon_instance.coupon_added
                + timezone.timedelta(days=coupon_instance.validity)
            ) < timezone.now().date():
                return Response({"error": "Invalid Coupon!"})

            # Calculation
            ordered_product_instance = OrderedProduct.objects.filter(
                consumer=request.user, status="cart"
            )

            total_price = get_price(ordered_product_instance, None)

            if not total_price:
                return Response({"error": "No Products in Cart!"})

            total_price = total_price["raw_price"]

            if total_price < coupon_instance.min_price:
                return Response({"error": "Buy More Products To Use This Coupon"})

            if total_price < coupon_instance.discount_bdt:
                return Response({"error": "You Cannot Use This Coupon"})

            ordered_product_instance.update(coupon_bdt=coupon_instance.discount_bdt)

            return Response({"status": "Coupon Code Used"})


class UseRewardsAPI(APIView):

    """
    POST for using rewards
    """

    permission_classes = [AuthenticateOnlyConsumer]

    def post(self, request, format=None, *args, **kwargs):
        consumer_instance = Consumer.objects.get(consumer=request.user)

        # Calculation
        reward_instance = Reward.objects.first()
        discount_amount = (
            consumer_instance.rewards / reward_instance.points
        ) * reward_instance.amount
        if discount_amount > reward_instance.max_amount:
            discount_amount = reward_instance.max_amount

        # Setting reward discount
        ordered_product_instance = OrderedProduct.objects.filter(
            consumer=request.user, status="cart"
        )

        total_price = get_price(ordered_product_instance, None)

        if total_price["total_price"] < discount_amount:
            return Response({"error": "You Cannot Use Rewards At This Moment"})

        ordered_product_instance.update(reward_discount=discount_amount)

        return Response({"status": "Used Rewards"})


# Update Realtime Visit
class VisitCountAPI(APIView):
    serializer_class = VisitCountSerializer

    def post(self, request, format=None, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid(raise_exception=True):
            try:
                instance = VisitCount.objects.get(
                    user_ref=serializer.data.get("user_ref")
                )
                instance.save()
                return Response({"status": "Updated"})

            except VisitCount.DoesNotExist:
                VisitCount.objects.create(
                    user_ref=serializer.data.get("user_ref"),
                )
                return Response({"status": "Created"})


# Login With Google
class GoogleLoginView(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    callback_url = "postmessage"
    client_class = OAuth2Client
