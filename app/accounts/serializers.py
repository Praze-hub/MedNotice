from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth import get_user_model
from accounts.enums import UserRole
from notification.tasks import send_password_reset_task
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_str, force_bytes
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator


CustomUser = get_user_model()

class PatientRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = CustomUser
        fields = ('email', 'password', 'password2', 'user_type')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password2": "Passwords do not match."})
        
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
      
        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            user_type=UserRole.PATIENT.value,
            is_verified=False,
            is_active=True
        )
        return user


class StaffOnboardingSerializer(serializers.ModelSerializer):
    user_type = serializers.ChoiceField(
        choices = [UserRole.DOCTOR.value, UserRole.ADMIN.value]
        
    )
    
    class Meta:
        model = CustomUser
        fields = ('email', 'user_type')
        
    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists")
        return value
    
    def create(self, validated_data):
        user_type = validated_data.get('user_type')
        
        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            password=None,
            user_type=user_type,
            is_staff=(user_type == UserRole.ADMIN.value),
            is_verified=(user_type != UserRole.DOCTOR.value),
            is_active=False
        )
        
        return user
    
class SetPasswordSerializer(serializers.Serializer):
     """Used by the doctor to set their password via invite link."""
     password = serializers.CharField(
         write_only=True, required=True, validators=[validate_password]
     )
     password2 = serializers.CharField(write_only=True, required=True)
     
     def validate(self, attrs):
         if attrs['password'] != attrs['password2']:
             raise serializers.ValidationError({"password2": "Password do not match"})
         
         return attrs
     

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()
    
    def validate_email(self, value):
        if not CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email does not exist.")
        return value
    
    def save(self, request=None):
        email = self.validated_data['email']
        user = CustomUser.objects.get(email=email)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        
        if request:
            base_url = f"{request.scheme}://{request.get_host()}"
        else:
            base_url = "http://localhost:8000"

        reset_url = f"{base_url}/api/v1/accounts/password-reset-confirm/?uid={uid}&token={token}"
        
        send_password_reset_task.delay(user.id, reset_url)
        return user
        
class PasswordResetConfirmSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True,
                                         min_length=8,
                                         validators=[validate_password],)
    
    def validate(self, attrs):
        try:
            uid = force_str(urlsafe_base64_decode(attrs['uid']))
            self.user = CustomUser.objects.get(pk=uid)
        except Exception:
            raise serializers.ValidationError({"uid": "Invalid uid"})
        
        if not default_token_generator.check_token(self.user, attrs['token']):
            raise serializers.ValidationError({"token": "Invalid or expired token"})
        
        return attrs
    
    def save(self):
        self.user.set_password(self.validated_data['new_password'])
        self.user.save(update_fields=["password"])
        return self.user
    

class ApproveDoctorSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)