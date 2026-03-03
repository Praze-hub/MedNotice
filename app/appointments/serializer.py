from appointments.services.scheduling import is_slot_available

from .models import Appointment
from patients.models import Patient
from rest_framework import serializers


class BaseAppointmentSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    status = serializers.CharField(read_only=True)

    def validate_scheduled_time(self, value):
        if not is_slot_available(value):
            raise serializers.ValidationError(
                "This time slot is already booked"
            )
        return value

class AppointmentSerializer(BaseAppointmentSerializer):
    patient_code = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = Appointment
        fields = ["id", "status", "scheduled_time", "description", "patient_code"]
        
    def create(self, validated_data):
        # Remove patient_code before model creation
        validated_data.pop("patient_code", None)
        return super().create(validated_data)
        
class AdminAppointmentSerializer(BaseAppointmentSerializer):
    patient_code = serializers.CharField(write_only=True)
    doctor_code = serializers.CharField(write_only=True)

    class Meta:
        model = Appointment
        fields = [
            "id",
            "status",
            "scheduled_time",
            "description",
            "patient_code",
            "doctor_code",
        ]
        
    def create(self, validated_data):
        # Remove non-model fields before creating Appointment
        validated_data.pop("patient_code", None)
        validated_data.pop("doctor_code", None)

        return super().create(validated_data)
    
class PatientAppointmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Appointment
        fields = ["id", "status", "scheduled_time", "description"]
        
    
class AppointmentCancelSerializer(serializers.Serializer):
    reason = serializers.CharField(max_length=500)
    
class AppointmentHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = [
            "id",
            "scheduled_time",
            "status",
            "cancellation_reason",
            "created_at",
        ]