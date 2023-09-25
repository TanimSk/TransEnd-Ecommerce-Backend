from rest_framework import serializers
from dj_rest_auth.registration.serializers import RegisterSerializer
from .models import Moderator, Notice, CouponCode
from productsAPI.models import Product, Category
from vendorAPI.models import Vendor
from userAPI.models import OrderedProduct
from .models import BookedCalls


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
            "admin_roles": self.validated_data.get("admin_roles", []),
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
            admin_roles=self.cleaned_data.get("admin_roles", []),
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
    price_usd = serializers.FloatField(required=False)
    price_gbp = serializers.FloatField(required=False)
    price_eur = serializers.FloatField(required=False)
    price_cad = serializers.FloatField(required=False)

    class Meta:
        exclude = (
            "product_added_date",
            "quantity_sold",
        )
        model = Product


class ManageProductViewSerializer(serializers.ModelSerializer):
    product_added_date = serializers.DateTimeField(format="%d/%m/%Y %I:%M %p")

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
    image_url = serializers.ListField(source="product.images")

    class Meta:
        fields = (
            "product_name",
            "product_id",
            "category_id",
            "ordered_quantity",
            "image_url",
            "ordered_date",
            "per_price",
            "total_price",
            "tracking_id",
            "status",
            "consumer_name",
            "consumer_phone",
            "consumer_email",
            "consumer_address",
            "special_instructions",
            "payment_method",
            "inside_dhaka",
            "order_total_price",
        )
        model = OrderedProduct


class VendorAnalyticsSerializer(serializers.ModelSerializer):
    vendor_name = serializers.CharField(source="product.vendor.name")
    product_name = serializers.CharField(source="product.name")

    class Meta:
        fields = (
            "vendor_name",
            "ordered_date",
            "product_name",
            "ordered_quantity",
            "total_price",
            "total_grant",
            "revenue",
        )
        model = OrderedProduct


class SpecificVendorAnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = Vendor


class PayVendorSerializer(serializers.Serializer):
    vendor_id = serializers.IntegerField(required=True)
    pay_amount = serializers.IntegerField(required=True)


# CD: create delete
class FeaturedCDProductSerializer(serializers.Serializer):
    product_id = serializers.IntegerField(required=True)


class FeaturedProductQuerySerializer(serializers.Serializer):
    vendor_id = serializers.IntegerField(required=True)
    category_id = serializers.IntegerField(required=True)
    product_name = serializers.CharField(required=True)


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ("admin_roles",)
        model = Moderator


class ManageAdminSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="moderator.email")

    class Meta:
        fields = (
            "email",
            "phone_number",
            "admin_roles",
        )
        model = Moderator


class BookedCallSerializer(serializers.ModelSerializer):
    book_on = serializers.DateTimeField(format="%d/%m/%Y %I:%M %p")

    class Meta:
        fields = "__all__"
        model = BookedCalls
