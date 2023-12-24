from rest_framework import serializers
from dj_rest_auth.registration.serializers import RegisterSerializer
from .models import Consumer, OrderedProduct, Wishlist
from userAPI.models import VisitCount


class WishlistSerializer(serializers.Serializer):
    category = serializers.IntegerField(source="product.category.id")
    id = serializers.IntegerField(source="product.id")
    images = serializers.ListField(source="product.images")
    name = serializers.CharField(source="product.name")
    price_bdt = serializers.IntegerField(source="product.price_bdt")
    wishlisted_date = serializers.DateTimeField(format="%d/%m/%Y %H:%M %p")

    class Meta:
        fields = ("category", "id", "images", "wishlisted_date", "name", "price_bdt")
        model = Wishlist


class ProfileSerializer(serializers.ModelSerializer):
    email_address = serializers.EmailField(read_only=True, source="consumer.email")
    rewards = serializers.IntegerField(read_only=True)

    class Meta:
        exclude = ("consumer",)
        model = Consumer


# Ordered Products
class OrderedProductSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(source="product.id", required=True)
    # read only fields
    category_id = serializers.IntegerField(source="product.category.id", read_only=True)
    name = serializers.CharField(source="product.name", read_only=True)
    img_urls = serializers.ListField(source="product.images", read_only=True)
    price_bdt = serializers.IntegerField(source="product.price_bdt", read_only=True)
    discount_percent = serializers.IntegerField(
        source="product.discount_percent", read_only=True
    )
    discount_max_bdt = serializers.IntegerField(
        source="product.discount_max_bdt", read_only=True
    )
    ordered_date = serializers.DateTimeField(format="%d/%m/%Y %I:%M %p", read_only=True)
    status = serializers.CharField(read_only=True)

    available_colors = serializers.IntegerField(source="product.colors", read_only=True)
    available_sizes = serializers.IntegerField(source="product.sizes", read_only=True)

    class Meta:
        fields = (
            "category_id",
            "product_id",
            "status",
            "ordered_quantity",
            "name",
            "img_urls",
            "price_bdt",
            "discount_percent",
            "discount_max_bdt",
            "ordered_date",
            "status",
            "order_total_price",
            "consumer_address",
            "inside_dhaka",
            "coupon_bdt",
            "reward_discount",
            "color",
            "size",
            "available_colors",
            "available_sizes",
        )
        model = OrderedProduct


# Custom Registration
class ConsumerCustomRegistrationSerializer(RegisterSerializer):
    consumer = serializers.PrimaryKeyRelatedField(
        read_only=True,
    )  # by default allow_null = False
    name = serializers.CharField(required=True)
    phone_number = serializers.IntegerField(required=True)
    address = serializers.CharField(required=True)
    # METHODS = (
    #     ("cod", "cod"),
    #     ("mobile", "mobile"),
    # )
    # payment_method = serializers.ChoiceField(choices=METHODS, required=False)
    # inside_dhaka = serializers.BooleanField(required=True)

    def get_cleaned_data(self):
        data = super(ConsumerCustomRegistrationSerializer, self).get_cleaned_data()
        extra_data = {
            "name": self.validated_data.get("name", ""),
            "phone_number": "mobile",
            "address": self.validated_data.get("address", ""),
            "payment_method": self.validated_data.get("payment_method", ""),
            "inside_dhaka": False,
        }
        data.update(extra_data)
        return data

    def save(self, request):
        user = super(ConsumerCustomRegistrationSerializer, self).save(request)
        user.is_consumer = True
        user.save()
        consumer = Consumer(
            consumer=user,
            name=self.cleaned_data.get("name"),
            phone_number=self.cleaned_data.get("phone_number"),
            address=self.cleaned_data.get("address"),
            payment_method=self.cleaned_data.get("payment_method"),
            inside_dhaka=self.cleaned_data.get("inside_dhaka"),
        )
        consumer.save()
        return user


class PlaceOrderSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            "consumer_name",
            "consumer_phone",
            "consumer_email",
            "consumer_address",
            "special_instructions",
            "payment_method",
            "inside_dhaka",
        )
        model = OrderedProduct


class CouponSerializer(serializers.Serializer):
    coupon_code = serializers.CharField(required=True)


class VisitCountSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ("user_ref",)
        model = VisitCount
