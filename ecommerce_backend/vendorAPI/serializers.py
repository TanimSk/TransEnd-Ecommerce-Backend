from rest_framework import serializers
from .models import Vendor


class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = Vendor

    def update(self, instance, validated_data):
        instance.name = validated_data.get("name")
        instance.phone_number = validated_data.get("phone_number")
        instance.address = validated_data.get("address")
        instance.save()
        return instance
