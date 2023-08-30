from dj_rest_auth.registration.views import RegisterView
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import AdminCustomRegistrationSerializer, NoticeSerializer
from django.utils.timezone import now
from .models import Notice

class AdminRegistrationView(RegisterView):
    serializer_class = AdminCustomRegistrationSerializer


class NoticeAPI(APIView):
    serializer_class = NoticeSerializer

    def get(self, request, format=None, *args, **kwargs):
        notice_instance = Notice.objects.filter(expiry_date__gt=now()).first()
        serialized_notice = self.serializer_class(notice_instance, many=False)
        return Response(serialized_notice.data)
    
    def post(self, request, format=None, *args, **kwargs):
        ...