from django.urls import path
from .views import AdminRegistrationView, NoticeAPI

urlpatterns = [
    path("registration/", AdminRegistrationView.as_view(), name="registration_admin"),
    path("notice/", NoticeAPI.as_view(), name="notice"),
    # path(""),
]
