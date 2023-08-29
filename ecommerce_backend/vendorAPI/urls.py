from django.urls import path
from .views import VendorAPI

urlpatterns = [
    path("", VendorAPI.as_view(), name="vendor"),
]
