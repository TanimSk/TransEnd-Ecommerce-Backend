from django.urls import path
from .views import (
    ConsumerRegistrationView,
    WishlistSerializerAPI,
    ProfileAPI,
    OrderProductAPI,
)

urlpatterns = [
    path(
        "registration/",
        ConsumerRegistrationView.as_view(),
        name="registration_consumer",
    ),
    path(
        "wishlist/",
        WishlistSerializerAPI.as_view(),
        name="wishlist",
    ),
    path(
        "profile/",
        ProfileAPI.as_view(),
        name="profile_info",
    ),
    path(
        "ordered_product/",
        OrderProductAPI.as_view(),
        name="ordered_products",
    ),
]
