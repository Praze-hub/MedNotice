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
    def send_doctor_approved_email(user):
        EmailService.send_html_email(
            subject="Your Doctor Account Has Been Approved 🎉",
            template="emails/doctor_approved.html",
            context={
                "user": user,
            },
            recipient_list=[user.email],
        )
        
    @staticmethod
    def send_appointment_created(appointment):
        # recipients = [
        #     appointment.patient.user.email,
        #     appointment.doctor.user.email,
        # ]
        EmailService.send_html_email(
            subject="Appointment Scheduled",
            template="emails/appointment_created.html",
            context={"appointment": appointment},
            recipient_list=[appointment.patient.user.email],
        )
        
        EmailService.send_html_email(
        subject="New Appointment Request",
        template="emails/appointment_request_doctor.html",
        context={"appointment": appointment},
        recipient_list=[appointment.doctor.user.email],
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
        
    @staticmethod
    def send_appointment_reminder(appointment):
        recipients = [appointment.patient.user.email]

        if appointment.doctor:
            recipients.append(appointment.doctor.user.email)

        EmailService.send_html_email(
            subject="Appointment Reminder",
            template="emails/appointment_reminder.html",
            context={"appointment": appointment},
            recipient_list=recipients,
        )
        
        
    @staticmethod
    def send_appointment_accepted(appointment):
        EmailService.send_html_email(
        subject="Appointment Confirmed",
        template="emails/appointment_accepted.html",
        context={"appointment": appointment},
        recipient_list=[appointment.patient.user.email],
        )
        
    @staticmethod
    def send_appointment_declined(appointment, reason):
        EmailService.send_html_email(
        subject="Appointment Request Declined",
        template="emails/appointment_declined.html",
        context={"appointment": appointment, "reason": reason},
        recipient_list=[appointment.patient.user.email],
    )