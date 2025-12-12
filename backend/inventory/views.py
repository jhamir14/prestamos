from rest_framework import viewsets
from .models import Moto
from .serializers import MotoSerializer

class MotoViewSet(viewsets.ModelViewSet):
    queryset = Moto.objects.all()
    serializer_class = MotoSerializer
