from django.urls import path
from .views import AdminRegistrationView, NoticeAPI, AdminAnalyticsAPI, AddProductsAPI, ManageCategoriesAPI

urlpatterns = [
    path("registration/", AdminRegistrationView.as_view(), name="registration_admin"),
    path("notice/", NoticeAPI.as_view(), name="notice"),
    path("analytics/", AdminAnalyticsAPI.as_view(), name="analytics"),
    path("add_product/", AddProductsAPI.as_view(), name="add_product"),
    path("manage_category/", ManageCategoriesAPI.as_view(), name="manage_category"),
]
