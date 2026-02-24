from django.utils import timezone
from appointments.enums import Status
from appointments.models import Appointment

def schedule_appointment(*, patient, scheduled_time, description):
    # if scheduled_time < timezone.now():
    #     raise ValueError("Cannot schedule appointment in the past")
    
    appointment = Appointment.objects.create(
                patient=patient,
                scheduled_time=scheduled_time,
                status=Status.SCHEDULED.value,
                description=description
            )
    
    return appointment


def is_slot_available(scheduled_time):
    return not Appointment.objects.filter(
        scheduled_time=scheduled_time,
        status=Status.SCHEDULED.value
    ).exists()