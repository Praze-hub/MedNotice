from rest_framework import viewsets, status
from rest_framework.response import Response

from .models import Patient
from .serializers import PatientSerializer

class PatientViewSet(viewsets.ModelViewSet):
    
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer