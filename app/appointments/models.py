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