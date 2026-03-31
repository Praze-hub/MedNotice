from celery import shared_task
from django.contrib.auth import get_user_model
from .services import EmailService
from appointments.models import Appointment

User = get_user_model()

@shared_task(bind=True, max_retries=3)
def send_verification_email_task(self, user_id, verification_url):
    try:
        user = User.objects.get(id=user_id)
        EmailService.send_verification_email(user, verification_url)
    except Exception as exc:
        self.retry(exc=exc, countdown=60)
        
@shared_task(bind=True, max_retries=3)
def send_appointment_created_task(self, appointment_id):
    try:
      
        appointment = Appointment.objects.select_related(
            "patient__user",
            "doctor__user",
        ).get(id=appointment_id)
        
        if not appointment.doctor:
            raise ValueError(f"Appointment {appointment_id} has no doctor assigned")
        
        EmailService.send_appointment_created(appointment)
    except Appointment.DoesNotExist:
        raise
    
    except Exception as exc:
        self.retry(exc=exc, countdown=60)
    
@shared_task(bind=True, max_retries=3)
def send_appointment_cancelled_task(self, appointment_id, reason):
    try:
      
        appointment = Appointment.objects.select_related(
            "patient__user",
            "doctor__user",
        ).get(id=appointment_id)
        EmailService.send_appointment_cancelled(appointment, reason)
        
    except Appointment.DoesNotExist:
        raise
    except Exception as exc:
        self.retry(exc=exc, countdown=60)
        
    
@shared_task(bind=True, max_retries=3)
def send_appointment_rescheduled_task(self, appointment_id):
    try:
        
        appointment = Appointment.objects.select_related(
            "patient__user",
            "doctor__user",
        ).get(id=appointment_id)
        
        if not appointment.doctor:
            raise ValueError(f"Appointment {appointment_id} has no doctor assigned")
        
    
        EmailService.send_appointment_rescheduled(appointment)
        
    except Appointment.DoesNotExist:
        raise 
    
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)