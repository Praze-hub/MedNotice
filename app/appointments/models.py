from django.db import models

from appointments.enums import Status
from common.models import BaseModel
from doctor.models import Doctor
from patients.models import Patient

class Appointment(BaseModel):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.PROTECT, related_name="doctor_appointments", null=True, blank=True)
    scheduled_time = models.DateTimeField()
    status = models.CharField(max_length=20,
                              choices=Status.choices(),
                              default=Status.SCHEDULED.value)
    description = models.CharField(max_length=500, null=True, blank=True)
    cancellation_reason = models.CharField(max_length=200, null=True, blank=True)
    
    def cancel(self, reason: str):
        if self.status == "completed":
            raise ValueError("Completed task cannot be cancelled")
        
        self.status = "cancelled"
        self.cancellation_reason = reason
        self.save(update_fields=["status", "cancellation_reason"])
        
    
    