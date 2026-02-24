from appointments.services.scheduling import is_slot_available

from .models import Appointment
from patients.models import Patient
from rest_framework import serializers

class AppointmentSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    status = serializers.CharField(read_only=True)
    
    class Meta:
        model = Appointment
        fields = ["id", "status", "scheduled_time", "description"]
        
    def validate_scheduled_time(self, value):
        if not is_slot_available(value):
            raise serializers.ValidationError(
                "This time slot is already booked"
            )
        return value
        
    
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