from celery import shared_task
from django.contrib.auth import get_user_model
from .services import EmailService

User = get_user_model()

@shared_task(bind=True, max_retries=3)
def send_verification_email_task(self, user_id, verification_url):
    try:
        user = User.objects.get(id=user_id)
        EmailService.send_verification_email(user, verification_url)
    except Exception as exc:
        self.retry(exc=exc, countdown=60)