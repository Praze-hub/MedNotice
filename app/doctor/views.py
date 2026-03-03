from accounts.enums import UserRole
from appointments.models import Appointment
from appointments.serializer import AppointmentHistorySerializer
from core.pagination import DefaultPagination
from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import action


from .models import Doctor
from .serializers import DoctorDashboardSerializer, DoctorSerializer

class DoctorViewSet(viewsets.GenericViewSet):
    
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = DefaultPagination
    
    def get_queryset(self):
        user = self.request.user
        
        # add pagination
        if user.user_type == UserRole.ADMIN.value:
            return Doctor.objects.all()
        
        return Doctor.objects.filter(user=user)
    
    @action(
        detail = False,
        methods = ['post'],
        url_path = 'doctor-profile',
    )
    def create_my_profile(self, request):
        if hasattr(request.user, "doctor_profile"):
            return Response(
                {"detail": "Doctor already exists"},
                status=status.HTTP_400_BAD_REQUEST,
            )
            
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        serializer.save(user=request.user)
        
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
        )
        
    @action(
        detail = False, 
        methods = ["get"], 
        url_path = "get-doctor-profile"
        )
    def get_profile(self, request):
        if not hasattr(request.user, "doctor_profile"):
            return Response(
                {"detail": "Doctor not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = self.get_serializer(request.user.doctor_profile)
        return Response(serializer.data)
    
    @action(
        detail = False, 
        methods=["get"], 
        url_path="dashboard"
    )
    def dashboard(self, request):
        if not hasattr(request.user, "doctor_profile"):
            return Response(
                {"detail": "Doctor not found"},
                status=404
            )
            
        doctor = request.user.doctor_profile
        
        # serializer = PatientDashboardSerializer(patient)
        
        # return Response(serializer.data)
        doctor_data = DoctorDashboardSerializer(doctor).data
        
        appointments = Appointment.objects.filter(
            doctor=doctor
        ).order_by("-scheduled_time")
        
        page = self.paginate_queryset(appointments)
        
        if page is not None:
            appointment_data = AppointmentHistorySerializer(page, many=True).data
            paginated_response = self.get_paginated_response(appointment_data)
            doctor_data["appointment_history"] = paginated_response.data
            return Response(doctor_data)
        
        appointment_data = AppointmentHistorySerializer(appointments, many=True).data
        doctor_data["appointment_history"] = appointment_data
        
        return Response(doctor_data)