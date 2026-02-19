from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.user_type == "admin":
            return True
        
        return obj.patient.user == request.user
        