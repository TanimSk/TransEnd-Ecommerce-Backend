from django.urls import path
from .views import (
    ConsumerRegistrationView,
    WishlistSerializerAPI,
    ProfileAPI,
    OrderProductAPI,
    CartAPI
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
        "cart/",
        CartAPI.as_view(),
        name="cart_products",
    ),
    path(
        "ordered_product/",
        OrderProductAPI.as_view(),
        name="ordered_products",
    ),
    path(
        "ordered_product/<str:method>",
        OrderProductAPI.as_view(),
        name="ordered_products",
    ),

]
