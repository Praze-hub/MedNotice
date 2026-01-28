from django.utils import timezone
from appointments.enums import Status
from appointments.models import Appointment

def schedule_appointment(*, patient, scheduled_time):
    # if scheduled_time < timezone.now():
    #     raise ValueError("Cannot schedule appointment in the past")
    
    appointment = Appointment.objects.create(
                patient=patient,
                scheduled_time=scheduled_time,
                status=Status.SCHEDULED.value
            )
    
    return appointment