from django.utils import timezone
from appointments.enums import Status
from appointments.models import Appointment
from doctor.models import DoctorShift
from datetime import datetime, timedelta
import pytz

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


# def is_slot_available(scheduled_time):
#     return not Appointment.objects.filter(
#         scheduled_time=scheduled_time,
#         status=Status.SCHEDULED.value
#     ).exists()
    
def get_doctor_available_slots(doctor, date):
    """
    Returns a list of available datetime slots for a doctor on a given date.
    Excludes slots already booked.
    """
    
    day_name = date.strftime("%A").lower()
    
    try:
        shift = DoctorShift.objects.get(doctor=doctor, day_of_week=day_name)
    except DoctorShift.DoesNotExist:
        return []
    
    slots = []
    slot_start = datetime.combine(date, shift.start_time)
    shift_end = datetime.combine(date, shift.end_time)
    
    while slot_start + timedelta(minutes=shift.slot_duration_minutes) <= shift_end:
        slot_end = slot_start + timedelta(minutes=shift.slot_duration_minutes)
        slots.append(slot_start)
        slot_start = slot_end
        
    booked_times = Appointment.objects.filter(
         doctor=doctor,
         scheduled_time__date=date,
         status__in=["pending", "scheduled"],
     ).values_list("scheduled_time", flat=True)
    
    booked_naive = [
        bt.astimezone(pytz.utc).replace(tzinfo=None) if bt.tzinfo else bt
        for bt in booked_times
    ] 
    
    available_slots = [slot for slot in slots if slot not in booked_naive]
    
    return available_slots


def is_slot_available(doctor, scheduled_time):
    """
    Checks if a specific datetime slot is available for a doctor.
    """  
    day_name = scheduled_time.strftime("%A").lower()
    
    try:
        shift = DoctorShift.objects.get(doctor=doctor, day_of_week=day_name)
    except DoctorShift.DoesNotExist:
        return False, "Doctor is not available on this day"
    
    slot_time = scheduled_time.time()
    if not (shift.start_time <= slot_time < shift.end_time):
        return False, f"Doctor is only availbable between {shift.start_time} and {shift.end_time}"
    
    already_booked = Appointment.objects.filter(
        doctor=doctor,
        scheduled_time=scheduled_time,
        status__in=["pending", "scheduled"],
    ).exists()
    
    if already_booked:
        return False, "This time slot is already booked"
    
    return True, None
    
    
    
    
