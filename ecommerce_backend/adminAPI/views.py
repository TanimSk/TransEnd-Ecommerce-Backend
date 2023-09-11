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
    OrderedProductsSerializer,
    CouponSerializer,
    ManageProductViewSerializer,
)
from productsAPI.serializers import ProductSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from django.utils.timezone import now
from django.db.models import Sum
from .models import Notice
from vendorAPI.models import Vendor
from productsAPI.models import Product, Category
from userAPI.models import OrderedProduct, Consumer
from rest_framework.pagination import PageNumberPagination


# Pagination Config
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 1
    page_size_query_param = "page_size"
    max_page_size = 10
    page_query_param = "p"


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


class ManageProductsAPI(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ManageProductViewSerializer

    def get(self, request, format=None, *args, **kwargs):
        products_instance = Product.objects.all()
        serialized_products = self.serializer_class(products_instance, many=True)
        return Response(serialized_products.data)

    def post(self, request, product_id=None, format=None, *args, **kwargs):
        if product_id is None:
            return Response({"status": "product_id missing"})

        product_instance = Product.objects.get(id=product_id)
        serialized_product = ProductSerializer(product_instance)
        return Response(serialized_product.data)

    def delete(self, request, product_id=None, format=None, *args, **kwargs):
        product_instance = Product.objects.get(id=product_id)
        product_instance.delete()
        return Response({"status": "Product Removed Successfully"})


class ManageOrdersAPI(APIView):

    """
    To set status to Delivered, post with customer_id
    """

    permission_classes = [IsAuthenticated]
    serializer_class = OrderedProductsSerializer

    def get(self, request, format=None, *args, **kwargs):
        customers_instance = (
            Consumer.objects.filter(consumer__order_consumer__isnull=False)
            .exclude(consumer__order_consumer__status="cart")
            .distinct()
        )

        # Paginating Result
        paginator = StandardResultsSetPagination()
        customers_instance_paginated = paginator.paginate_queryset(
            customers_instance, request
        )

        response_array = []
        for customer_instance in customers_instance_paginated:
            # Product Details
            products_instance = OrderedProduct.objects.filter(
                consumer__consumer=customer_instance
            )
            serialized_products = OrderedProductsSerializer(
                products_instance, many=True
            )
            total_payment = OrderedProduct.objects.filter(
                consumer__consumer=customer_instance
            ).aggregate(total_payment=Sum("total_price"))

            response_array.append(
                {
                    "customer_details": {
                        "id": customer_instance.id,
                        "name": customer_instance.name,
                        "phone_number": customer_instance.phone_number,
                        "address": customer_instance.address,
                        "payment_method": customer_instance.payment_method,
                        "inside_dhaka": customer_instance.inside_dhaka,
                    },
                    "tracking_id": serialized_products.data[0]["tracking_id"],
                    "status": serialized_products.data[0]["status"],
                    "products": serialized_products.data,
                    **total_payment,
                }
            )

        return paginator.get_paginated_response(response_array)

    def post(self, request, consumer_id=None, format=None, *args, **kwargs):
        consumer_instance = Consumer.objects.get(id=consumer_id)
        ordered_product_instance = (
            OrderedProduct.objects.filter(consumer__consumer=consumer_instance)
            .exclude(status="cart")
            .exclude(status="delivered")
        )
        ordered_product_instance.update(status="delivered")

        return Response({"status": "Successfully Delivered"})


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
