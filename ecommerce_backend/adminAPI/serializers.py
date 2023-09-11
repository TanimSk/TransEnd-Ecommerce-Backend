from rest_framework import serializers
from dj_rest_auth.registration.serializers import RegisterSerializer
from .models import Moderator, Notice, CouponCode
from productsAPI.models import Product, Category
from vendorAPI.models import Vendor
from userAPI.models import OrderedProduct


class AdminCustomRegistrationSerializer(RegisterSerializer):
    moderator = serializers.PrimaryKeyRelatedField(
        read_only=True,
    )  # by default allow_null = False
    phone_number = serializers.IntegerField(required=True)
    admin_roles = serializers.ListField(child=serializers.CharField(), required=False)

    def get_cleaned_data(self):
        data = super(AdminCustomRegistrationSerializer, self).get_cleaned_data()
        extra_data = {
            "phone_number": self.validated_data.get("phone_number", ""),
            "admin_roles": self.validated_data.get("admin_roles", ""),
        }
        data.update(extra_data)
        return data

    def save(self, request):
        user = super(AdminCustomRegistrationSerializer, self).save(request)
        user.is_admin = True
        user.save()
        admin = Moderator(
            moderator=user,
            phone_number=self.cleaned_data.get("phone_number"),
            admin_roles=self.cleaned_data.get("admin_roles"),
        )
        admin.save()
        return user


class NoticeSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = Notice


class AdminAnalyticsSerializer(serializers.Serializer):
    from_date = serializers.DateField()
    to_date = serializers.DateField()


class AddProductsSerializer(serializers.ModelSerializer):
    class Meta:
        exclude = (
            "product_added_date",
            "quantity_sold",
        )
        model = Product


class ManageProductViewSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            "id",
            "name",
            "price_bdt",
            "quantity",
            "product_added_date",
        )
        model = Product


class ManageCategoriesSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = Category


class ManageVendorsSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = Vendor


class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = CouponCode


class OrderedProductsSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name")
    product_id = serializers.IntegerField(source="product.id")
    category_id = serializers.IntegerField(source="product.category.id")

    class Meta:
        fields = (
            "product_name",
            "product_id",
            "category_id",
            "ordered_quantity",
            "ordered_date",
            "per_price",
            "total_price",
            "tracking_id",
            "status",
        )
        model = OrderedProduct
