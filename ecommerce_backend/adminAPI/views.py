from dj_rest_auth.registration.views import RegisterView
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import (
    AdminCustomRegistrationSerializer,
    NoticeSerializer,
    AdminAnalyticsSerializer,
    AddProductsSerializer,
    ManageCategoriesSerializer,
    ManageVendorsSerializer,
    CouponSerializer
)
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from django.utils.timezone import now
from django.db.models import Sum
from .models import Notice
from vendorAPI.models import Vendor
from productsAPI.models import Product, Category
from userAPI.models import OrderedProduct


class AdminRegistrationView(RegisterView):
    serializer_class = AdminCustomRegistrationSerializer


class NoticeAPI(APIView):
    serializer_class = NoticeSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, format=None, *args, **kwargs):
        notice_instance = Notice.objects.filter(expiry_date__gt=now()).first()
        serialized_notice = self.serializer_class(notice_instance, many=False)
        return Response(serialized_notice.data)

    def post(self, request, format=None, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid(raise_exception=True):
            Notice.objects.create(**serializer.data)
            return Response({"status": "Successfully Added Product"})



class AdminAnalyticsAPI(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AdminAnalyticsSerializer

    def post(self, request, format=None, *args, **kwargs):
        serializer = AdminAnalyticsSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            available_products = Product.objects.filter(quantity__gt=0).aggregate(
                available_products=Sum("quantity")
            )["available_products"]
            sold_products = Product.objects.aggregate(
                sold_products=Sum("quantity_sold")
            )["sold_products"]

            orders_instance = OrderedProduct.objects.filter(
                ordered_date__range=[
                    serializer.data.get("from_date"),
                    serializer.data.get("to_date"),
                ]
            )
            orders_placed = (
                orders_instance.exclude(status="cart")
                .exclude(status="delivered")
                .aggregate(orders_placed=Sum("ordered_quantity"))
            )["orders_placed"]

            orders_delivered = orders_instance.filter(status="delivered").aggregate(
                orders_delivered=Sum("ordered_quantity")
            )["orders_delivered"]
            total_revenue = orders_instance.aggregate(
                total_revenue=Sum("product__price_bdt")
            )["total_revenue"]
            total_grant = orders_instance.aggregate(total_grant=Sum("product__grant"))[
                "total_grant"
            ]

            return Response(
                {
                    "available_products": available_products,
                    "sold_products": sold_products,
                    "orders_placed": orders_placed,
                    "orders_delivered": orders_delivered,
                    "total_revenue": total_revenue,
                    "total_grant": total_grant,
                }
            )


class AddProductsAPI(APIView):

    """
    Get Categories list on get request,
    use that category list to post products
    """

    permission_classes = [IsAuthenticated]
    serializer_class = AddProductsSerializer

    def post(self, request, format=None, *args, **kwargs):
        serializer = AddProductsSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            print(serializer.data)
            Product.objects.create(
                name=serializer.data.get("name"),
                details=serializer.data.get("details", ""),
                tags=serializer.data.get("tags", []),
                # Price
                price_bdt=serializer.data.get("price_bdt"),
                price_usd=serializer.data.get("price_usd", 0),
                price_gbp=serializer.data.get("price_gbp", 0),
                price_eur=serializer.data.get("price_eur", 0),
                price_cad=serializer.data.get("price_cad", 0),
                images=serializer.data.get("images", []),
                quantity=serializer.data.get("quantity"),
                rewards=serializer.data.get("rewards", 0),
                grant=serializer.data.get("grant", 0),
                # Discount
                discount_percent=serializer.data.get("discount_percent", 0),
                discount_max_bdt=serializer.data.get("discount_max_bdt", 0),
                # Foreign Keys
                category=Category.objects.get(id=serializer.data.get("category")),
                vendor=Vendor.objects.get(id=serializer.data.get("vendor")),
            )
            return Response({"status": "Successfully Added Product"})

    def get(self, request, format=None, *args, **kwargs):
        vendors_instance = Vendor.objects.all().values("name", "id")
        categories_instance = Category.objects.all().values("name", "id")

        return Response(
            {"vendors": list(vendors_instance), "category": list(categories_instance)}
        )


class ManageCategoriesAPI(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ManageCategoriesSerializer

    def get(self, request, format=None, *args, **kwargs):
        category_instance = Category.objects.all()
        serialized_category = ManageCategoriesSerializer(category_instance, many=True)
        return Response(serialized_category.data)

    def post(self, request, format=None, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid(raise_exception=True):
            Category.objects.create(**serializer.data)
            return Response({"status": "Successfully Added Product"})


class ManageVendorsAPI(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ManageVendorsSerializer

    def get(self, request, format=None, *args, **kwargs):
        vendor_instance = Vendor.objects.all()
        serialized_category = ManageVendorsSerializer(vendor_instance, many=True)
        return Response(serialized_category.data)

    def post(self, request, format=None, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid(raise_exception=True):
            Vendor.objects.create(**serializer.data)
            return Response({"status": "Successfully Added Vendor"})


class CouponAPI(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CouponSerializer

    def post(self, request, format=None, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid(raise_exception=True):
            CouponSerializer.objects.create(**serializer.data)
            return Response({"status": "Successfully Added Coupon Code"})

