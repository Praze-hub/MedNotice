from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .enums import UserRole
from django.utils import timezone
from .managers import CustomUserManager


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    user_type = models.CharField(max_length=10, choices=UserRole.choices(), default=UserRole.ADMIN.value)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    
    objects = CustomUserManager()
    
    USERNAME_FIELD = 'email' 
    REQUIRED_FIELDS = ['user_type']
    
    def __str__(self):
        return f"{self.email} ({self.user_type})"
    
    
    
    
    