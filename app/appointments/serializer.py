from .models import Appointment
from patients.models import Patient
from rest_framework import serializers

class AppointmentSerializer(serializers.ModelSerializer):
    patient_code = serializers.CharField(write_only=True)
    
    class Meta:
        model = Appointment
        fields = ["patient", "patient_code", "status", "scheduled_time"]
        read_only = ["patient"]
        
    def create(self, validated_data):
        patient_code = validated_data.pop("patient_code")
        patient = Patient.objects.get(patient_code=patient_code)
        validated_data["patient"] = patient
        return super().create(validated_data)
    
class AppointmentCancelSerializer(serializers.Serializer):
    reason = serializers.CharField(max_length=500)