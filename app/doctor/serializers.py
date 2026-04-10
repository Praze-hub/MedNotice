from appointments.models import Appointment
from appointments.serializer import AppointmentHistorySerializer
from .models import Doctor
from rest_framework import serializers


class DoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = [
            "id",
            "doctor_code",
            "first_name",
            "last_name",
            "phone_number",
            "email",
            "date_of_birth",
            "specialization",
            "years_of_experience",
            "consultation_fee",
            "is_available",
        ]
        read_only_fields = ["id", "doctor_code"]