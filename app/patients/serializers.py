from appointments.models import Appointment
from appointments.serializer import AppointmentHistorySerializer

from .models import Patient
from rest_framework import serializers


class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = [
            "id",
            "patient_code",
            "first_name",
            "last_name",
            "phone_number",
            "email",
        ]
        
        read_only_fields = ["id", "patient_code"]
        
class PatientDashboardSerializer(serializers.ModelSerializer):
    age = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Patient
        fields = [
            "patient_code",
            "first_name",
            "last_name",
            "phone_number",
            "date_of_birth",
            "age",
            "blood_type",
            "allergies",
            "chronic_conditions",
        ]
        
   