from django.urls import path
from .views import CategoryAPI, SearchAPI, FeaturedProductAPI, FilterAPI

urlpatterns = [
    path("categories/", CategoryAPI.as_view(), name="category"),
    path("categories/<int:category_id>", CategoryAPI.as_view(), name="category"),
    path(
        "categories/<int:category_id>/<int:product_id>",
        CategoryAPI.as_view(),
        name="category",
    ),
    path(
        "categories/<int:category_id>/filter/<str:param>",
        FilterAPI.as_view(),
        name="filter_product",
    ),
    
    path("search/", SearchAPI.as_view(), name="search"),
    path("featured_products/<str:section>", FeaturedProductAPI.as_view(), name="featured_products"),
]
