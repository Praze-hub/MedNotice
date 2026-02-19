from django.db import models, transaction
from common.models import BaseModel
from core import settings

class Patient(BaseModel):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="patient_profile", null=True, blank=True)
    patient_code = models.CharField(max_length=50, unique=True, editable=False)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    
    def save(self, *args, **kwargs):
        with transaction.atomic():
            creating = self.pk is None
            super().save(*args, **kwargs)
            
            if creating and not self.patient_code:
                self.patient_code = f"PAT-{self.id:06d}"
                super().save(update_fields=["patient_code"])
