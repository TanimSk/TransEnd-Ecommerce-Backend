from django.urls import path
from .views import (
    AdminRegistrationView,
    NoticeAPI,
    AdminAnalyticsAPI,
    AddProductsAPI,
    ManageCategoriesAPI,
    ManageVendorsAPI,
    CouponAPI,
    ManageOrdersAPI
)

urlpatterns = [
    path("registration/", AdminRegistrationView.as_view(), name="registration_admin"),
    path("notice/", NoticeAPI.as_view(), name="notice"),
    path("analytics/", AdminAnalyticsAPI.as_view(), name="analytics"),
    path("add_product/", AddProductsAPI.as_view(), name="add_product"),
    path("manage_category/", ManageCategoriesAPI.as_view(), name="manage_category"),
    path("manage_order/", ManageOrdersAPI.as_view(), name="manage_order"),
    path("manage_vendor/", ManageVendorsAPI.as_view(), name="manage_vendor"),
    path("add_coupon/", CouponAPI.as_view(), name="add_coupon"),
]
