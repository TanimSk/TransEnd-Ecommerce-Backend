from rest_framework import serializers
from dj_rest_auth.registration.serializers import RegisterSerializer
# from rest_framework.authtoken.models import Token

from .models import Consumer


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
