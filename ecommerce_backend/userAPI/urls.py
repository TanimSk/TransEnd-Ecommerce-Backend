from django.urls import path
from .views import ConsumerRegistrationView

urlpatterns = [
    path(
        "registration/",
        ConsumerRegistrationView.as_view(),
        name="registration_consumer",
    ),
]
