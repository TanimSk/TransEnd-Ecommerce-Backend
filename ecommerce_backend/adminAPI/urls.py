from django.urls import path
from .views import (
    AdminRegistrationView,
    NoticeAPI,
    AdminAnalyticsAPI,
    AddProductsAPI,
    ManageCategoriesAPI,
    ManageVendorsAPI,
    CouponAPI,
    ManageOrdersAPI,
    ManageProductsAPI,
    VendorAnalyticsAPI,
    SpecificVendorAnalyticsAPI,
    FeaturedProductAPI,
    FeaturedProductQueryAPI,
    PermissionsAPI,
    ManageAdminAPI,
    CallBookingAPI
)

urlpatterns = [
    path("registration/", AdminRegistrationView.as_view(), name="registration_admin"),
    path("notice/", NoticeAPI.as_view(), name="notice"),
    path("analytics/", AdminAnalyticsAPI.as_view(), name="analytics"),
    path("add_product/", AddProductsAPI.as_view(), name="add_product"),
    path("manage_category/", ManageCategoriesAPI.as_view(), name="manage_category"),
    # Manage Products
    path("manage_product/", ManageProductsAPI.as_view(), name="manage_product"),
    path(
        "manage_product/<int:product_id>",
        ManageProductsAPI.as_view(),
        name="manage_product",
    ),
    path("manage_order/", ManageOrdersAPI.as_view(), name="manage_order"),
    path(
        "manage_order/<uuid:order_tracking_id>", ManageOrdersAPI.as_view(), name="manage_order"
    ),
    path("manage_vendor/", ManageVendorsAPI.as_view(), name="manage_vendor"),
    # Vendor Analytics
    path("vendor_analytics/", VendorAnalyticsAPI.as_view(), name="vendor_analytics"),
    path(
        "vendor_analytics/specific/<str:phone_number>",
        SpecificVendorAnalyticsAPI.as_view(),
        name="vendor_specific_analytics",
    ),
    # Featured Product
    path(
        "featured_products/<str:section>",
        FeaturedProductAPI.as_view(),
        name="featured_products",
    ),
    path(
        "featured_products/<str:section>/<int:product_id>",
        FeaturedProductAPI.as_view(),
        name="featured_products_delete",
    ),

    path(
        "featured_products_query/",
        FeaturedProductQueryAPI.as_view(),
        name="featured_products_query",
    ),
    path("add_coupon/", CouponAPI.as_view(), name="add_coupon"),
    path("permissions/", PermissionsAPI.as_view(), name="permissions"),
    # Manage Admin
    path("manage_admin/", ManageAdminAPI.as_view(), name="manage_admin"),
    
    # Booked Call
    path("book_call/", CallBookingAPI.as_view(), name="book_call"),
]
