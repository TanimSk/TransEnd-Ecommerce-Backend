from django.urls import path
from .views import CategoryAPI, SearchAPI, FeaturedProductAPI

urlpatterns = [
    path("categories/", CategoryAPI.as_view(), name="category"),
    path("categories/<int:category_id>", CategoryAPI.as_view(), name="category"),
    path(
        "categories/<int:category_id>/filter/<str:param>",
        CategoryAPI.as_view(),
        name="category",
    ),
    path(
        "categories/<int:category_id>/<int:product_id>",
        CategoryAPI.as_view(),
        name="category",
    ),
    path("search/", SearchAPI.as_view(), name="search"),
    path("featured_products/<str:section>", FeaturedProductAPI.as_view(), name="featured_products"),
]
