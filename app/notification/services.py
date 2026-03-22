from django.core.mail import send_mail
from django.conf import settings
import sendgrid
from sendgrid.helpers.mail import Mail
from sendgrid import SendGridAPIClient

class EmailService:
    @staticmethod
    def send_email(subject, message, recipient_list):
        message = Mail(
            from_email=settings.DEFAULT_FROM_EMAIL,
            to_emails=recipient_list,
            subject=subject,
            plain_text_content=message,
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
        subject = "Verify your email"
        message = f"Click the link to verify your email {verification_url}"
        
        return EmailService.send_email(
            subject,
            message,
            [user.email]
        )