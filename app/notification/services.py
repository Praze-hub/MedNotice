from django.core.mail import send_mail
from django.conf import settings
import sendgrid
from sendgrid.helpers.mail import Mail
from sendgrid import SendGridAPIClient
from django.template.loader import render_to_string

class EmailService:
    @staticmethod
    def send_html_email(subject, template, context, recipient_list):
        html_content = render_to_string(template, context)
        message = Mail(
            from_email=settings.DEFAULT_FROM_EMAIL,
            to_emails=recipient_list,
            subject=subject,
            html_content=html_content,
        )
        
        try:
            sg = SendGridAPIClient(settings.EMAIL_HOST_PASSWORD)
            response = sg.send(message)
            return response.status_code
        except Exception as e:
            print("Email error:", str(e))
            raise
            
    
    
    @staticmethod
    def send_verification_email(user, verification_url):
        
        return EmailService.send_html_email(
            subject="Verify your email",
            template="emails/verify_email.html",
            context={
                "title": "Verify your Email",
                "verification_url": verification_url
            },
            recipient_list=[user.email]
        )
        
    @staticmethod
    def send_appointment_created(appointment):
        recipients = [
            appointment.patient.user.email,
            appointment.doctor.user.email,
        ]
        EmailService.send_html_email(
            subject="Appointment Scheduled",
            template="emails/appointment_created.html",
            context={"appointment": appointment},
            recipient_list=recipients,
        )
        
    @staticmethod
    def send_appointment_cancelled(appointment, reason):
        recipients = [
            appointment.patient.user.email,
        ]
        
        if appointment.doctor:
            recipients.append(appointment.doctor.user.email)
            
        EmailService.send_html_email(
            subject="Appointment Cancelled",
            template="emails/appointment_cancelled.html",
            context={
                "appointment": appointment,
                "reason": reason
            },
            recipient_list=recipients,
        )
        
    @staticmethod
    def send_appointment_rescheduled(appointment):
        recipients = [
            appointment.patient.user.email,
            appointment.doctor.user.email,
        ]
        EmailService.send_html_email(
            subject="Appointment Rescheduled",
            template="emails/appointment_reschedule.html",
            context={"appointment": appointment},
            recipient_list=recipients,
        )