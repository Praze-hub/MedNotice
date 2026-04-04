# from ..accounts.enums import UserRole
# from rest_framework.permissions import BasePermission

# class IsAdmin(BasePermission):
#      def has_permission(self, request, view):
#         return request.user.user_type == UserRole.ADMIN
    
# class IsPatient(BasePermission):
#     def has_permission(self, request, view):
#         return request.user.user_type == UserRole.PATIENT
    
# class IsDoctor(BasePermission):
#     def has_permission(self, request, view):
#         return request.user.user_type == UserRole.DOCTOR
    
# class IsVerifiedDoctor(BasePermission):
#     def has_permission(self, request, view):
#         user = request.user
#         return(
#             user.is_authenticated and
#             user.user_type == "doctor" and
#             user.is_verified
#         )
    
    
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