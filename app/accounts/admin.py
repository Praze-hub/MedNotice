from django.contrib import admin
from .models import CustomUser

@admin.register(CustomUser)
class PatientAdmin(admin.ModelAdmin):
    list_display = ("email", "user_type", "is_verified")
    

