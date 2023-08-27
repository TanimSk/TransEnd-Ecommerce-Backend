from dj_rest_auth.registration.views import RegisterView
from .serializers import AdminCustomRegistrationSerializer


class AdminRegistrationView(RegisterView):
    serializer_class = AdminCustomRegistrationSerializer
