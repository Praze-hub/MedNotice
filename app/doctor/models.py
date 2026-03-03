from django.db import models, transaction
from common.models import BaseModel
from core import settings

class Doctor(BaseModel):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="doctor_profile", null=True, blank=True)
    doctor_code = models.CharField(max_length=50, unique=True, editable=False)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    date_of_birth = models.DateField(null=True, blank=True)
    specialization = models.CharField(max_length=100)
    license_number = models.CharField(max_length=100, unique=True)
    years_of_experience = models.PositiveIntegerField(default=0)
    consultation_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    is_available = models.BooleanField(default=True)
  

    
    def save(self, *args, **kwargs):
        with transaction.atomic():
            creating = self.pk is None
            super().save(*args, **kwargs)
            
            if creating and not self.doctor_code:
                self.doctor_code = f"DOC-{self.id:06d}"
                super().save(update_fields=["doctor_code"])
