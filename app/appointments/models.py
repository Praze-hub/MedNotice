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
                              default=Status.PENDING.value)
    description = models.CharField(max_length=500, null=True, blank=True)
    cancellation_reason = models.CharField(max_length=200, null=True, blank=True)
    decline_reason = models.TextField(blank=True, null=True) 
    reminder_sent = models.BooleanField(default=False)
    
    def cancel(self, reason: str):
        if self.status == Status.COMPLETED.value:
            raise ValueError("Completed appointments cannot be cancelled")
        
        if self.status == Status.DECLINED.value:
            raise ValueError("Declined appointments cannot be cancelled")
        
        self.status = Status.CANCELLED.value
        self.cancellation_reason = reason
        self.save(update_fields=["status", "cancellation_reason"])
        
    def accept(self):
        if self.status != Status.PENDING.value:
            raise ValueError("Only pending appointments can be accepted")
        
        self.status = Status.SCHEDULED.value
        self.save(update_fields=["status"])
    
    def decline(self, reason: str):
        if self.status != Status.PENDING.value:
            raise ValueError("Only pending appointments can be accepted")
        
        self.status = Status.DECLINED.value
        self.decline_reason = reason
        self.save(update_fields=["status", "decline_reason"])
        
    def __str__(self):
        return f"Appointment {self.id} | {self.patient} -> {self.doctor} | {self.status}"
    