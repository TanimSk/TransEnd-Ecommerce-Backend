from dj_rest_auth.registration.views import RegisterView
from .serializers import ConsumerCustomRegistrationSerializer


class ConsumerRegistrationView(RegisterView):
    serializer_class = ConsumerCustomRegistrationSerializer
