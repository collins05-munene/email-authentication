from django.core.mail import send_mail
from django.conf import settings

class EmailService:

    @staticmethod
    def send_otp(email, otp):
        subject = "Your Login OTP"
        message = f"""
            Your OTP code is {otp}.
            This code will expire in 5 minutes.
            If you did not request this, ignore this email.
        """
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email], fail_silently=False)