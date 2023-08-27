"""
URL configuration for ecommerce_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from dj_rest_auth.registration.views import VerifyEmailView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("products/", include("productsAPI.urls")),
    # ---------- Auth ------------
    path("rest-auth/", include("dj_rest_auth.urls")),
    path(
        "rest-auth/registration/account-confirm-email/",
        VerifyEmailView.as_view(),
        name="account_email_verification_sent",
    ),
    path("get-access-token/", TokenRefreshView.as_view(), name="get-access-token"),
    
    path("administrator/", include("adminAPI.urls")),
    path("consumer/", include("userAPI.urls")),
]
