from notification.services import EmailService
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken
from django.utils.encoding import smart_str
# from rest_framework_simplejwt.views import TokenObtainPairView
from django.core.mail import send_mail
from .serializers import RegisterSerializer, PasswordResetRequestSerializer, PasswordResetConfirmSerializer 
from notification.tasks import send_doctor_approved_email_task, send_verification_email_task
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404



CustomUser = get_user_model()

class RegisterView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer
    
    def perform_create(self, serializer):
        user = serializer.save()
        token = RefreshToken.for_user(user).access_token
        current_site = get_current_site(self.request).domain
        relative_link = reverse('verify-email')
        verification_url = f"http://{current_site}{relative_link}?token={str(token)}"
        
       
        send_verification_email_task.delay(user.id, verification_url)
        
class VerifyEmail(APIView):
    def get(self, request):
        token = request.GET.get('token')
        try:
            access_token = AccessToken(token)
            user_id = access_token['user_id']
            user = CustomUser.objects.get(id=user_id)
            user.is_active = True
            user.save()
            return Response({'message': 'Email verified successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': 'Invalid token or user'}, status=status.HTTP_400_BAD_REQUEST)
        
class PasswordResetRequestView(generics.GenericAPIView):
    serializer_class = PasswordResetRequestSerializer
    
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message': 'Password reset link sent to your email.'}, status=status.HTTP_200_OK)
    
class PasswordResetConfirmView(generics.GenericAPIView):
    serializer_class = PasswordResetConfirmSerializer
    
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message': 'Password has been reset successfully'}, status=status.HTTP_200_OK)
        
class AdminViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAdminUser]
    
    @action(detail=True, 
            methods=["post"], 
            url_path="approve-doctor")
    def approve_doctor(self, request, pk=None):
        try:
            user = CustomUser.objects.get(pk=pk)
        except CustomUser.DoesNotExist:
            return Response({"detail": "User not found"}, status=404)
        
        print(f"DEBUG: Found user {user.email}, user_type={user.user_type}, is_verified={user.is_verified}")
        
        if user.user_type != "doctor":
            return Response(
                {"detail": "This user is not a doctor"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.is_verified = True
        user.save(update_fields=["is_verified"])
        
        send_doctor_approved_email_task.delay(user.id)
        
        user.refresh_from_db()
        print(f"DEBUG: After save, is_verified={user.is_verified}")
        
        return Response(
            {"message": "Doctor approved successfully"},
            status=status.HTTP_200_OK
        )
    