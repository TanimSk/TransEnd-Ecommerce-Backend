from rest_framework import serializers
from dj_rest_auth.registration.serializers import RegisterSerializer
from .models import Consumer, OrderedProduct


class WishlistSerializer(serializers.Serializer):
    product_id = serializers.IntegerField(required=True)


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        exclude = ("consumer",)
        model = Consumer


# Ordered Products
class OrderedProductSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(source="product.id", required=True)

    # read only fields
    name = serializers.CharField(source="product.name", read_only=True)
    img_urls = serializers.ListField(source="product.images", read_only=True)
    added_on = serializers.DateTimeField(source="ordered_date", read_only=True)

    class Meta:
        fields = (
            "product_id",
            "ordered_quantity",
            "name",
            "img_urls",
            "added_on",
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
    METHODS = (
        ("cod", "cod"),
        ("mobile", "mobile"),
    )
    payment_method = serializers.ChoiceField(choices=METHODS)
    inside_dhaka = serializers.BooleanField(required=True)

    def get_cleaned_data(self):
        data = super(ConsumerCustomRegistrationSerializer, self).get_cleaned_data()
        extra_data = {
            "name": self.validated_data.get("name", ""),
            "phone_number": self.validated_data.get("phone_number", ""),
            "address": self.validated_data.get("address", ""),
            "payment_method": self.validated_data.get("payment_method", ""),
            "inside_dhaka": self.validated_data.get("inside_dhaka", ""),
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
