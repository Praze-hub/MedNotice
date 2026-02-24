from xml.dom import ValidationErr

from django.shortcuts import get_object_or_404
from accounts.enums import UserRole
from appointments.enums import Status
from patients.models import Patient
from .services.scheduling import is_slot_available, schedule_appointment
from .serializer import AppointmentCancelSerializer, AppointmentSerializer
from .models import Appointment
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .permissions import IsAdmin, IsPatient
from rest_framework.exceptions import PermissionDenied, ValidationError


class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        if user.user_type == UserRole.ADMIN.value:
            return Appointment.objects.all()
        
        return Appointment.objects.filter(
            patient__user=user
        )
    
    def perform_create(self, serializer):
        user = self.request.user
        print(user)
        
        if user.user_type == UserRole.ADMIN.value:
            patient_code = self.request.data.get("patient_code")
            
            if not patient_code:
                raise ValidationError("patient_code is required for admin scheduling")

            try:
                patient = Patient.objects.get(patient_code=patient_code)
            except Patient.DoesNotExist:
                raise ValidationError("Patient not found")

            serializer.save(patient=patient)
            return
        
        if user.user_type != UserRole.PATIENT.value:
            raise PermissionDenied("Only patients can create appointments")
        
        if not hasattr(user, "patient_profile"):
            raise PermissionDenied("Patient profile not created")
        
        serializer.save(patient=user.patient_profile)
    
    @action(
        detail = True,
        methods = ["post"],
        url_path = 'cancel-appointment',
        serializer_class=AppointmentCancelSerializer
    )
   
    def cancel_appointment(self, request, pk=None):
        appointment = self.get_object()
        
        serializer = AppointmentCancelSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            appointment.cancel(
                reason = serializer.validated_data["reason"]
            )
        except ValueError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        return Response(
            {
                "appointment_id": appointment.id,
                "status": appointment.status,
                "cancellation_reason": appointment.cancellation_reason,
            },
            status=status.HTTP_200_OK
        )
        
    @action(
        detail=True,
        methods=["post"],
        url_path="reschedule",
        serializer_class=AppointmentSerializer
    )
    
    def reschedule(self, request, pk=None):
        appointment = self.get_object()
        
        if appointment.status != Status.SCHEDULED.value:
            return Response(
                {"detail": "Only scheduled appointments can be rescheduled"},
                status=400
            )
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        new_time = serializer.validated_data["scheduled_time"]
        
        appointment.scheduled_time = new_time
        appointment.save(update_fields=['scheduled_time'])
        
        return Response(
            AppointmentSerializer(appointment).data,
            status=status.HTTP_200_OK
        )
