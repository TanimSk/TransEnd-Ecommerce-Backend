from rest_framework.response import Response
from .serializers import VendorSerializer
from rest_framework.views import APIView
from .models import Vendor


class VendorAPI(APIView):
    serializer_class = VendorSerializer

    def get(self, request, format=None, *args, **kwargs):
        vendors_instance = Vendor.objects.all()
        serialized_vendors = self.serializer_class(vendors_instance, many=True)
        return Response(serialized_vendors.data)

    # def post(self, request, format=None, *args, **kwargs):
    #     ...
