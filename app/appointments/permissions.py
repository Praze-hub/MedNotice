from accounts.enums import UserRole
from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.user_type == UserRole.ADMIN.value
        )


class IsPatient(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.user_type == UserRole.PATIENT.value
        )


class IsDoctor(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.user_type == UserRole.DOCTOR.value
        )


class IsVerifiedDoctor(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.user_type == UserRole.DOCTOR.value 
            and request.user.is_verified
        )