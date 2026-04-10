from appointments.models import Appointment
from appointments.serializer import AppointmentHistorySerializer

from .models import Patient
from rest_framework import serializers

class PatientSerializer(serializers.ModelSerializer):
    age = serializers.IntegerField(read_only=True)

    class Meta:
        model = Patient
        fields = [
            "id",
            "patient_code",
            "first_name",
            "last_name",
            "phone_number",
            "email",
            "date_of_birth",
            "age",
            "blood_type",
            "allergies",
            "chronic_conditions",
        ]
        read_only_fields = ["id", "patient_code", "age"]
        
   