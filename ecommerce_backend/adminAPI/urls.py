from django.urls import path
from .views import AdminRegistrationView

urlpatterns = [
    path("registration/", AdminRegistrationView.as_view(), name="registration_admin"),
]
