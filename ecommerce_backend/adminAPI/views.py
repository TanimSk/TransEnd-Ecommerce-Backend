from dj_rest_auth.registration.views import RegisterView
from rest_framework.response import Response
from rest_framework.views import APIView
from productsAPI.serializers import FeaturedProductSerializer, ProductQuerySerializer
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
    VendorAnalyticsSerializer,
    SpecificVendorAnalyticsSerializer,
    PayVendorSerializer,
    FeaturedCDProductSerializer,
    FeaturedProductQuerySerializer,
    PermissionSerializer,
    ManageAdminSerializer,
    BookedCallSerializer,
    ChangeStatusSerializer,
    HeroContentSerializer,
)

# from productsAPI.serializers import ProductSerializer
from rest_framework.permissions import (
    IsAuthenticatedOrReadOnly,
    BasePermission,
)
from django.utils import timezone
from django.db.models import Sum, F, Count
from .models import Notice, CouponCode, Moderator, BookedCall, HeroContent
from userAPI.models import VisitCount
from vendorAPI.models import Vendor
from productsAPI.models import Product, Category, FeaturedProduct
from userAPI.models import OrderedProduct, Consumer, OrderPackageTrack
from rest_framework.pagination import PageNumberPagination


# Pagination Config
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 12
    page_query_param = "p"


# Authenticate Admin Only Class
class AuthenticateOnlyAdmin(BasePermission):
    def has_permission(self, request, view):
        if request.user and request.user.is_authenticated:
            if request.user.is_admin:
                return True
            else:
                return False
        return False


class AdminRegistrationView(RegisterView):
    serializer_class = AdminCustomRegistrationSerializer


class NoticeAPI(APIView):
    serializer_class = NoticeSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, format=None, *args, **kwargs):
        notice_instance = Notice.objects.first()
        serialized_notice = self.serializer_class(notice_instance, many=False)

        if notice_instance is not None:
            if (
                notice_instance.expiry_date < timezone.now()
                or notice_instance.notice == ""
            ):
                valid = False
            else:
                valid = True
            return Response({**serialized_notice.data, "valid": valid})

        else:
            return Response(
                {"notice": "", "expiry_date": timezone.now(), "valid": False}
            )

    def post(self, request, format=None, *args, **kwargs):
        if not request.user.is_admin:
            return Response({"error": "Logged in user is not admin!"})

        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid(raise_exception=True):
            notice_instance = Notice.objects.first()
            if notice_instance is not None:
                notice_instance.notice = serializer.data.get("notice")
                notice_instance.expiry_date = serializer.data.get("expiry_date")
                notice_instance.save()
                return Response({"status": "Successfully Updated Notice"})
            else:
                Notice.objects.create(**serializer.data)
                return Response({"status": "Successfully Created Notice"})


class AdminAnalyticsAPI(APIView):
    permission_classes = [AuthenticateOnlyAdmin]
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
                    timezone.datetime.strptime(
                        serializer.data.get("from_date"), "%Y-%m-%d"
                    ).date(),
                    timezone.datetime.strptime(
                        serializer.data.get("to_date"), "%Y-%m-%d"
                    ).date()
                    + timezone.timedelta(days=1),
                ]
            )

            orders_placed = (
                orders_instance.exclude(status="cart")
                .exclude(status="delivered")
                .values("tracking_id")
                .annotate(Count("tracking_id"))
            )

            orders_placed = orders_placed.count()

            orders_delivered = (
                orders_instance.filter(status="delivered")
                .values("tracking_id")
                .annotate(Count("tracking_id"))
            ).count()

            total_revenue = orders_instance.aggregate(total_revenue=Sum("revenue"))[
                "total_revenue"
            ]
            total_grant = orders_instance.aggregate(total_grant=Sum("total_grant"))[
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

    permission_classes = [AuthenticateOnlyAdmin]
    serializer_class = AddProductsSerializer

    def post(self, request, format=None, *args, **kwargs):
        serializer = AddProductsSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            # print(serializer.data)
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
                added_by=request.user,
            )
            return Response({"status": "Successfully Added Product"})

    def get(self, request, format=None, *args, **kwargs):
        vendors_instance = Vendor.objects.all().values("name", "id")
        categories_instance = Category.objects.all().values("name", "id")

        return Response(
            {"vendors": list(vendors_instance), "category": list(categories_instance)}
        )


class ManageCategoriesAPI(APIView):
    permission_classes = [AuthenticateOnlyAdmin]
    serializer_class = ManageCategoriesSerializer

    def get(self, request, format=None, *args, **kwargs):
        category_instance = Category.objects.all().order_by("-id")
        serialized_category = ManageCategoriesSerializer(category_instance, many=True)
        return Response(serialized_category.data)

    def post(self, request, category_id=None, format=None, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            if category_id is None:
                Category.objects.create(**serializer.data)
                return Response({"status": "Successfully Created A Category"})
            else:
                category_instance = Category.objects.get(id=category_id)
                category_instance.name = serializer.data.get("name")
                category_instance.images = serializer.data.get("images")
                category_instance.save()
                return Response({"status": "Successfully Updated"})

    def delete(self, request, category_id=None, format=None, *args, **kwargs):
        if category_id is None:
            return Response({"error": "Category Id missing"})

        count = Product.objects.filter(category__id=category_id).count()
        Category.objects.get(id=category_id).delete()
        if count == 0:
            return Response({"status": f"Successfully Removed Category"})
        return Response(
            {"status": f"Successfully Removed Category and {count} product(s)"}
        )


class ManageProductsAPI(APIView):

    """
    get request with no params, returns all products.
    get request with params (product_id), returns that products details.
    use post request to update that product.
    delete with product_id param.
    For filtering pass category name in params. ?category=<category_name>
    """

    permission_classes = [AuthenticateOnlyAdmin]
    serializer_class = AddProductsSerializer

    def get(self, request, product_id=None, format=None, *args, **kwargs):
        if product_id is None:
            if not request.GET.get("category", "") == "":
                products_instance = Product.objects.filter(
                    category=request.GET.get("category", "")
                ).order_by("-product_added_date")
            else:
                products_instance = Product.objects.all().order_by(
                    "-product_added_date"
                )

            serialized_products = ManageProductViewSerializer(
                products_instance, many=True
            )
            return Response(serialized_products.data)

        product_instance = Product.objects.get(id=product_id)
        serialized_product = AddProductsSerializer(product_instance)
        return Response(serialized_product.data)

    # Update a Product
    def post(self, request, product_id=None, format=None, *args, **kwargs):
        if product_id is None:
            return Response({"error": "product_id missing"})

        product_instance = Product.objects.get(id=product_id)
        serializer = AddProductsSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            # print(serializer.data)

            product_instance.name = serializer.data.get("name")
            product_instance.details = serializer.data.get("details", "")
            product_instance.tags = serializer.data.get("tags", [])
            # Price
            product_instance.price_bdt = serializer.data.get("price_bdt")
            product_instance.price_usd = serializer.data.get("price_usd", 0)
            product_instance.price_gbp = serializer.data.get("price_gbp", 0)
            product_instance.price_eur = serializer.data.get("price_eur", 0)
            product_instance.price_cad = serializer.data.get("price_cad", 0)
            product_instance.images = serializer.data.get("images", [])
            product_instance.quantity = serializer.data.get("quantity")
            product_instance.rewards = serializer.data.get("rewards", 0)
            product_instance.grant = serializer.data.get("grant", 0)
            # Discount
            product_instance.discount_percent = serializer.data.get(
                "discount_percent", 0
            )
            product_instance.discount_max_bdt = serializer.data.get(
                "discount_max_bdt", 0
            )
            # Foreign Keys
            product_instance.category = Category.objects.get(
                id=serializer.data.get("category")
            )
            product_instance.vendor = Vendor.objects.get(
                id=serializer.data.get("vendor")
            )

            # Update
            product_instance.save()

            return Response({"status": "Product Updated Successfully"})

    # Delete a Product
    def delete(self, request, product_id=None, format=None, *args, **kwargs):
        if product_id is None:
            return Response({"error": "product_id missing"})

        product_instance = Product.objects.get(id=product_id)
        product_instance.delete()
        return Response({"status": "Product Removed Successfully"})


class ManageOrdersAPI(APIView):

    """
    To set status to Delivered, post with order_tracking_id.
    For getting filtered GET response, pass ?method=cod | ?method=paid | ?method=delivered
    """

    permission_classes = [AuthenticateOnlyAdmin]
    # serializer_class = OrderedProductsSerializer

    def get(self, request, format=None, *args, **kwargs):
        # Getting Individual Customers with ordered product
        tracker_instance = OrderPackageTrack.objects.all().order_by("-id")

        # Paginating Result
        paginator = StandardResultsSetPagination()
        tracker_instance_paginated = paginator.paginate_queryset(
            tracker_instance, request
        )

        response_array = []
        for tracker_instance in tracker_instance_paginated:
            if not request.GET.get("method", "") == "":
                # Filtering
                products_instance = OrderedProduct.objects.filter(
                    tracking_id=tracker_instance.tracking_id,
                    status=request.GET.get("method", ""),
                )

            else:
                # Product Details
                products_instance = OrderedProduct.objects.filter(
                    tracking_id=tracker_instance.tracking_id
                )

            if products_instance.exists():
                serialized_products = OrderedProductsSerializer(
                    products_instance, many=True
                )

                response_array.append(
                    {
                        "customer_details": {
                            "name": serialized_products.data[0]["consumer_name"],
                            "phone_number": serialized_products.data[0][
                                "consumer_phone"
                            ],
                            "address": serialized_products.data[0]["consumer_address"],
                            "payment_method": serialized_products.data[0][
                                "payment_method"
                            ],
                            "inside_dhaka": serialized_products.data[0][
                                "consumer_name"
                            ],
                        },
                        "tracking_id": serialized_products.data[0]["tracking_id"],
                        "status": serialized_products.data[0]["status"],
                        "products": serialized_products.data,
                        "delivery_charge": serialized_products.data[0]["courier_fee"],
                        "coupon": serialized_products.data[0]["coupon_bdt"],
                        "reward_discount": serialized_products.data[0][
                            "reward_discount"
                        ],
                        "total_payment": serialized_products.data[0][
                            "order_total_price"
                        ],
                        "instructions": serialized_products.data[0][
                            "special_instructions"
                        ],
                    }
                )

        return paginator.get_paginated_response(response_array)

    # Set Order To Delivered & Dispatched
    def post(self, request, order_tracking_id=None, format=None, *args, **kwargs):
        if order_tracking_id is None:
            return Response({"error": "Order Tracking ID param is missing"})

        serialized_data = ChangeStatusSerializer(data=request.data)

        if serialized_data.is_valid(raise_exception=True):
            ordered_product_instance = OrderedProduct.objects.filter(
                tracking_id=order_tracking_id
            ).exclude(status="cart")

            if serialized_data.data.get("status") == "delivered":
                ordered_product_instance = ordered_product_instance.exclude(
                    status="delivered"
                )
                ordered_product_instance.update(status="delivered")
                return Response({"status": "Successfully Delivered"})

            elif serialized_data.data.get("status") == "dispatched":
                ordered_product_instance = ordered_product_instance.exclude(
                    status="dispatched"
                )
                ordered_product_instance.update(status="dispatched")
                return Response({"status": "Successfully Dispatched"})


class ManageVendorsAPI(APIView):
    permission_classes = [AuthenticateOnlyAdmin]
    serializer_class = ManageVendorsSerializer

    def get(self, request, format=None, *args, **kwargs):
        vendor_instance = Vendor.objects.all().order_by("-id")
        serialized_category = ManageVendorsSerializer(vendor_instance, many=True)
        return Response(serialized_category.data)

    def post(self, request, vendor_id=None, format=None, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid(raise_exception=True):
            if vendor_id is None:
                Vendor.objects.create(**serializer.data)
                return Response({"status": "Successfully Added Vendor"})

            else:
                vendor_instance = Vendor.objects.get(id=vendor_id)
                serializer.update(vendor_instance, serializer.data)
                # vendor_instance.name = serializer.data.get("name")
                # vendor_instance.phone_number = serializer.data.get("phone_number")
                # vendor_instance.address = serializer.data.get("address")
                # vendor_instance.save()
                return Response({"status": "Successfully Updated"})

    def delete(self, request, vendor_id=None, format=None, *args, **kwargs):
        if vendor_id is None:
            return Response({"error": "Vendor Id Missing"})

        Vendor.objects.get(id=vendor_id).delete()
        return Response({"status": "Successfully Removed Vendor"})


class CouponAPI(APIView):
    permission_classes = [AuthenticateOnlyAdmin]
    serializer_class = CouponSerializer

    def get(self, request, format=None, *args, **kwargs):
        coupons_instance = CouponCode.objects.all().order_by("-coupon_added")
        serialized_coupons = CouponSerializer(coupons_instance, many=True)
        return Response(serialized_coupons.data)

    def delete(self, request, coupon_id=None, format=None, *args, **kwargs):
        if coupon_id is None:
            return Response({"error": "Coupon id missing"})

        if CouponCode.objects.filter(id=coupon_id).exists():
            CouponCode.objects.get(id=coupon_id).delete()
            return Response({"status": "Successfully Removed Coupon"})

        return Response({"error": "Invalid Coupon Id"})

    def post(self, request, format=None, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid(raise_exception=True):
            coupon_instance = CouponCode.objects.filter(
                code=serializer.data.get("code")
            ).first()
            if coupon_instance is not None:
                coupon_instance.discount_bdt = serializer.data.get("discount_bdt")
                coupon_instance.validity = serializer.data.get("validity")
                coupon_instance.min_price = serializer.data.get("min_price")
                coupon_instance.save()
                return Response({"status": "Successfully Updated Coupon"})

            CouponCode.objects.create(**serializer.data)
            return Response({"status": "Successfully Added Coupon Code"})


class VendorAnalyticsAPI(APIView):
    permission_classes = [AuthenticateOnlyAdmin]
    serializer_class = AdminAnalyticsSerializer

    def post(self, request, format=None, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid(raise_exception=True):
            orders_instance = OrderedProduct.objects.filter(
                ordered_date__range=[
                    timezone.datetime.strptime(
                        serializer.data.get("from_date"), "%Y-%m-%d"
                    ).date(),
                    timezone.datetime.strptime(
                        serializer.data.get("to_date"), "%Y-%m-%d"
                    ).date()
                    + timezone.timedelta(days=1),
                ]
            )
            serialized_analytics = VendorAnalyticsSerializer(orders_instance, many=True)
            return Response(serialized_analytics.data)


class SpecificVendorAnalyticsAPI(APIView):

    """
    You will get vendor info on get request
    use vendor id and amount to pay on post request
    """

    permission_classes = [AuthenticateOnlyAdmin]
    serializer_class = PayVendorSerializer

    def get(self, request, phone_number=None, format=None, *args, **kwargs):
        if phone_number is None:
            return Response({"error": "phone_number param is missing!"})

        vendor_instance = Vendor.objects.filter(phone_number=phone_number).first()
        if vendor_instance is None:
            return Response({"error": "No Vendors Found!"})

        serialized_vendor = SpecificVendorAnalyticsSerializer(vendor_instance)

        # Calculations
        product_instance = Product.objects.filter(vendor=vendor_instance)

        if product_instance.count() == 0:
            return Response(
                {**serialized_vendor.data, "status": "This Vendor Has No Product!"}
            )

        sold_products = product_instance.aggregate(sold_products=Sum("quantity_sold"))[
            "sold_products"
        ]
        available_products = product_instance.aggregate(
            available_products=Sum("quantity")
        )["available_products"]

        amount_be_paid = (
            product_instance.aggregate(amount=Sum(F("grant") * F("quantity_sold")))[
                "amount"
            ]
            - vendor_instance.total_received_money
        )

        return Response(
            {
                **serialized_vendor.data,
                "sold_products": sold_products,
                "unsold_products": available_products,
                "amount_to_be_paid": amount_be_paid,
            }
        )

    def post(self, request, format=None, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid(raise_exception=True):
            vendor_instance = Vendor.objects.get(id=serializer.data.get("vendor_id"))
            vendor_instance.total_received_money += serializer.data.get("pay_amount")
            vendor_instance.save()

            return Response({"status": "Updated!"})


class FeaturedProductAPI(APIView):

    """
    Shows available featured products on get request,
    you can delete them by passing param.
    post with `product_id` for adding.
    """

    permission_classes = [AuthenticateOnlyAdmin]
    serializer_class = FeaturedCDProductSerializer

    def get(self, request, section=None, format=None, *args, **kwargs):
        if section == "home" or section == "category":
            products_instance = FeaturedProduct.objects.filter(section=section)
            serialized_products = FeaturedProductSerializer(
                products_instance, many=True
            )
            return Response(serialized_products.data)

        return Response({"error": "Wrong Params!"})

    def post(self, request, section=None, format=None, *args, **kwargs):
        if section == "home" or section == "category":
            serializer = self.serializer_class(data=request.data)

            if serializer.is_valid(raise_exception=True):
                product_instance = Product.objects.get(
                    id=serializer.data.get("product_id")
                )
                if FeaturedProduct.objects.filter(
                    product=product_instance, section=section
                ).exists():
                    return Response({"error": "Already exists in featured products"})

                FeaturedProduct.objects.create(
                    product=product_instance, section=section
                )
                return Response({"status": "Added To Featured Products Successfully!"})

        return Response({"error": "Wrong Params!"})

    def delete(
        self, request, section=None, product_id=None, format=None, *args, **kwargs
    ):
        if (product_id is not None) and (section == "home" or section == "category"):
            product_instance = Product.objects.get(id=product_id)
            FeaturedProduct.objects.filter(
                product=product_instance, section=section
            ).first().delete()

            return Response({"status": "Removed From Featured Products Successfully!"})

        return Response({"error": "Wrong Params!"})


class FeaturedProductQueryAPI(APIView):

    """
    vendors and categories will be showed on get, (for dropdown) on get req
    query result will be shown on post req
    """

    permission_classes = [AuthenticateOnlyAdmin]
    serializer_class = FeaturedProductQuerySerializer

    def get(self, request, format=None, *args, **kwargs):
        vendors_instance = Vendor.objects.all().values("name", "id")
        categories_instance = Category.objects.all().values("name", "id")
        return Response(
            {"vendors": list(vendors_instance), "category": list(categories_instance)}
        )

    def post(self, request, format=None, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid(raise_exception=True):
            product_instance = Product.objects.filter(
                name__icontains=serializer.data.get("product_name"),
                category_id=serializer.data.get("category_id"),
                vendor_id=serializer.data.get("vendor_id"),
            )

            serialized_products = ProductQuerySerializer(product_instance, many=True)
            return Response(serialized_products.data)


class PermissionsAPI(APIView):
    permission_classes = [AuthenticateOnlyAdmin]

    def get(self, request, format=None, *args, **kwargs):
        admin_instance = Moderator.objects.get(moderator=request.user)
        serializer = PermissionSerializer(admin_instance)
        return Response(serializer.data)


class ManageAdminAPI(APIView):
    permission_classes = [AuthenticateOnlyAdmin]
    serializer_class = ManageAdminSerializer

    def get(self, request, format=None, *args, **kwargs):
        moderator_instance = Moderator.objects.all().order_by("-id")
        serialized_moderators = ManageAdminSerializer(moderator_instance, many=True)
        return Response(serialized_moderators.data)

    def post(self, request, admin_id=None, format=None, *args, **kwargs):
        if admin_id is None:
            return Response({"error": "Admin Id Missing"})

        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            moderator_instance = Moderator.objects.get(id=admin_id)
            moderator_instance.admin_roles = serializer.data.get("admin_roles")
            moderator_instance.save()
            return Response({"status": "Successfully Updated"})


# Booking Call
class CallBookingAPI(APIView):
    serializer_class = BookedCallSerializer

    def get(self, request, format=None, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_admin:
            calls_instance = BookedCall.objects.all().order_by("-book_on")
            serialized_calls = BookedCallSerializer(calls_instance, many=True)
            return Response(serialized_calls.data)

        return Response({"error": "You Do Not Have The Permission!"})

    def post(self, request, format=None, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid(raise_exception=True):
            BookedCall.objects.create(**serializer.data)
            return Response({"status": "Booked For A Call"})


# Realtime Visit
class GetVisitAPI(APIView):
    permission_classes = [AuthenticateOnlyAdmin]

    def get(self, request, format=None, *args, **kwargs):
        users_instance = VisitCount.objects.filter(
            last_visit__gte=timezone.now() - timezone.timedelta(minutes=5)
        )
        return Response({"current_user": users_instance.count()})


# Hero Content
class HeroContentAPI(APIView):
    def get(self, request, format=None, *args, **kwargs):
        return Response(HeroContentSerializer(HeroContent.objects.first()).data)

    def post(self, request, format=None, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response({"error": "Not authenticated"})

        serialized_data = HeroContentSerializer(data=request.data)
        if serialized_data.is_valid(raise_exception=True):
            hero_instance = HeroContent.objects.first()

            if hero_instance is None:
                HeroContent.objects.create(**serialized_data.data)
                return Response({"status": "Successfully Created Hero Content!"})

            hero_instance.images = serialized_data.data.get("images")
            hero_instance.main_heading = serialized_data.data.get("main_heading")
            hero_instance.primary_heading = serialized_data.data.get("primary_heading")
            hero_instance.secondary_heading = serialized_data.data.get(
                "secondary_heading"
            )

            hero_instance.save()
            return Response({"status": "Successfully Updated Hero Content!"})
