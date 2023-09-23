from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from dj_rest_auth.registration.views import VerifyEmailView
from rest_framework.documentation import include_docs_urls
from rest_framework_simplejwt.views import TokenVerifyView
from userAPI.views import GoogleLoginView
from dj_rest_auth.views import PasswordResetConfirmView

# --------------- Google Login ---------------
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import RedirectView


class UserRedirectView(LoginRequiredMixin, RedirectView):
    """
    This view is needed by the dj-rest-auth-library in order to work the google login. It's a bug.
    """

    permanent = False

    def get_redirect_url(self):
        return "redirect-url"


urlpatterns = [
    path("", include_docs_urls(title="API Documentation")),
    path("admin/", admin.site.urls),
    path("products/", include("productsAPI.urls")),
    # ---------- Auth ------------
    path("rest-auth/", include("dj_rest_auth.urls")),
    path(
        "rest-auth/registration/account-confirm-email/",
        VerifyEmailView.as_view(),
        name="account_email_verification_sent",
    ),
    path('rest-auth/password/reset/confirm/<str:uidb64>/<str:token>', PasswordResetConfirmView.as_view(),
            name='password_reset_confirm'),
    


    path("rest-auth/google/login/", GoogleLoginView.as_view(), name="google_login"),
    path("~redirect/", UserRedirectView.as_view(), name="redirect"),
    path("get-access-token/", TokenRefreshView.as_view(), name="get-access-token"),
    path("api/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("administrator/", include("adminAPI.urls")),
    path("consumer/", include("userAPI.urls")),
    path("vendor/", include("vendorAPI.urls")),
]
