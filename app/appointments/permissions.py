from accounts.enums import UserRole
from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):
     def has_permission(self, request):
        return request.user.user_type == UserRole.ADMIN
    
class IsPatient(BasePermission):
    def has_permission(self, request):
        return request.user.user_type == UserRole.PATIENT
    
class IsDoctor(BasePermission):
    def has_permission(self, request):
        return request.user.user_type == UserRole.DOCTOR
        