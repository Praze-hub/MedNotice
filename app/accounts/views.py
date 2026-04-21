from accounts.enums import UserRole
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
from django.core.mail import send_mail
from .serializers import ApproveDoctorSerializer, PatientRegisterSerializer, PasswordResetRequestSerializer, PasswordResetConfirmSerializer, SetPasswordSerializer, StaffOnboardingSerializer 
from notification.tasks import send_doctor_approved_email_task, send_staff_invite_task, send_verification_email_task
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str


CustomUser = get_user_model()

class PatientRegisterView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = PatientRegisterSerializer
    
    def perform_create(self, serializer):
        user = serializer.save()
        token = RefreshToken.for_user(user).access_token
        current_site = get_current_site(self.request).domain
        relative_link = reverse('verify-email')
        verification_url = f"http://{current_site}{relative_link}?token={str(token)}"
        
       
        send_verification_email_task.delay(user.id, verification_url)
        
class StaffOnboardingView(generics.CreateAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = StaffOnboardingSerializer
    
    def perform_create(self, serializer):
        user = serializer.save()
        
        token_generator = PasswordResetTokenGenerator()
        token = token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        
        
        current_site = get_current_site(self.request).domain
        invite_url = f"http://{current_site}/api/v1/accounts/auth/set-password/?uid={uid}&token={token}"

        send_staff_invite_task.delay(user.id, invite_url)
        
        
class SetPasswordView(APIView):
    """
    Called when the doctor clicks the invite link in their email.
    Validates the token and lets them set their password.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        uid = request.query_params.get('uid')
        token = request.query_params.get('token')

        if not uid or not token:
            return Response(
                {"detail": "Invalid invite link."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user_id = force_str(urlsafe_base64_decode(uid))
            user = CustomUser.objects.get(pk=user_id)
        except (CustomUser.DoesNotExist, ValueError):
            return Response(
                {"detail": "Invalid invite link."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        token_generator = PasswordResetTokenGenerator()
        if not token_generator.check_token(user, token):
            return Response(
                {"detail": "Invite link is invalid or has expired."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = SetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user.set_password(serializer.validated_data['password'])
        user.is_active = True 
        user.save(update_fields=['password', 'is_active'])

        return Response(
            {"detail": "Password set successfully. You can now log in."},
            status=status.HTTP_200_OK,
        )
        
class VerifyEmail(APIView):
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        token = request.GET.get('token')
        try:
            access_token = AccessToken(token)
            user_id = access_token['user_id']
            user = CustomUser.objects.get(id=user_id)
            
            user.is_verified = True
            user.save()
            return Response({'message': 'Email verified successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': 'Invalid token or user'}, status=status.HTTP_400_BAD_REQUEST)
        
class PasswordResetRequestView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = PasswordResetRequestSerializer
    
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message': 'Password reset link sent to your email.'}, status=status.HTTP_200_OK)
    
class PasswordResetConfirmView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = PasswordResetConfirmSerializer
    
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message': 'Password has been reset successfully'}, status=status.HTTP_200_OK)
    
    
class AdminViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = ApproveDoctorSerializer

    @action(
        detail=False,
        methods=["post"],
        url_path="approve-doctor",
    )
    def approve_doctor(self, request):
        serializer = ApproveDoctorSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)  

        email = serializer.validated_data["email"]  

        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return Response(
                {"detail": "User not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        if user.user_type != UserRole.DOCTOR.value:
            return Response(
                {"detail": "This user is not a doctor"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if user.is_verified:
            return Response(
                {"detail": "This doctor is already verified"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.is_verified = True
        user.save(update_fields=["is_verified"])

        send_doctor_approved_email_task.delay(user.id)

        return Response(
            {"message": "Doctor approved successfully", "email": user.email},
            status=status.HTTP_200_OK,
        )