from django.shortcuts import get_object_or_404
from patients.models import Patient
from .services.scheduling import schedule_appointment
from .serializer import AppointmentCancelSerializer, AppointmentSerializer
from .models import Appointment
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .permissions import IsAdmin


class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
    
    def get_queryset(self):
        user = self.request.user
        
        if user.user_type == "admin":
            return Appointment.objects.all()
        
        return Appointment.objects.filter(
            patient__user=user
        )
    
    @action(
        detail = True,
        methods = ['get', 'post'],
        url_path = 'book-appointment',
        serializer_class=AppointmentSerializer,
    )
    def book_appointment(self, request, pk=None):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # patient = get_object_or_404(Patient, pk=pk)
        user = request.user
        
        if user.user_type != "patient":
            return Response(
                {"detail": "Only patients can book appointments"},
                status=status.HTTP_403_FORBIDDEN,
            )
            
        if not hasattr(user, "patient_profile"):
            return Response(
                {"detail": "Patient profile not created"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        appointment = schedule_appointment(
            patient = user.patient_profile,
            scheduled_time = serializer.validated_data["scheduled_time"],
        )
        
        return Response(
            {
                "appointment_id": appointment.id,
                 "status": appointment.status
            },
            status=status.HTTP_201_CREATED
        )
        
    """
    Add appointment id and patient id for the cancellation
    """
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
        
