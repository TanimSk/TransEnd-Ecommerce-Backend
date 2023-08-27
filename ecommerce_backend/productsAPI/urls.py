from django.urls import path
from .views import CategoryAPI

urlpatterns = [
    path("categories/", CategoryAPI.as_view(), name="category"),
    path("categories/<int:category_id>", CategoryAPI.as_view(), name="category"),
    path(
        "categories/<int:category_id>/<int:product_id>",
        CategoryAPI.as_view(),
        name="category",
    ),
]
