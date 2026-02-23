from accounts.enums import UserRole
from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import action


from .models import Patient
from .serializers import PatientDashboardSerializer, PatientSerializer

class PatientViewSet(viewsets.GenericViewSet):
    
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        # add pagination
        if user.user_type == UserRole.ADMIN.value:
            return Patient.objects.all()
        
        return Patient.objects.filter(user=user)
    
    @action(
        detail = False,
        methods = ['post'],
        url_path = 'patient-profile',
    )
    def create_my_profile(self, request):
        if hasattr(request.user, "patient_profile"):
            return Response(
                {"detail": "Profile already exists"},
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
        url_path = "get-patient-profile"
        )
    def get_profile(self, request):
        if not hasattr(request.user, "patient_profile"):
            return Response(
                {"detail": "Profile not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = self.get_serializer(request.user.patient_profile)
        return Response(serializer.data)
    
    @action(
        detail = False, 
        methods=["get"], 
        url_path="dashboard"
    )
    def dashboard(self, request):
        if not hasattr(request.user, "patient_profile"):
            return Response(
                {"detail": "Profile not found"},
                status=404
            )
            
        patient = request.user.patient_profile
        
        serializer = PatientDashboardSerializer(patient)
        
        return Response(serializer.data)