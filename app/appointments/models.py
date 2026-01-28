from django.db import models

from appointments.enums import Status
from common.models import BaseModel
from patients.models import Patient

class Appointment(BaseModel):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    scheduled_time = models.DateTimeField()
    status = models.CharField(max_length=20,
                              choices=Status.choices(),
                              default=Status.SCHEDULED.value)
    cancellation_reason = models.CharField(max_length=200, null=True)
    
    def cancel(self, reason: str):
        if self.status == "completed":
            raise ValueError("Completed task cannot be cancelled")
        
        self.status = "cancelled"
        self.cancellation_reason = reason
        self.save(update_fields=["status", "cancellation_reason"])
        
    
    