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