import secrets
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password

from ..models import EmailOTP
from ..constants import OTP_LENGTH, OTP_EXPIRY_MINUTES

class OTPService:
    @staticmethod
    def generate_otp():
        return str(secrets.randbelow(10 ** OTP_LENGTH)).zfill(OTP_LENGTH)
    
    @staticmethod
    def create_otp_record(email, purpose="login", ip=None, user_agent=None):
        otp = OTPService.generate_otp()

        record = EmailOTP.objects.create(
            email=email,
            hashed_otp=make_password(otp),
            purpose=purpose,
            expires_at=timezone.now() + timedelta(minutes=OTP_EXPIRY_MINUTES),
            ip_address = ip,
            user_agent=user_agent,
        )

        return otp, record
    
    @staticmethod
    def verify_otp(email, otp, purpose="login"):
        try:
            record = EmailOTP.objects.filter(
                email=email,
                purpose=purpose,
                is_used=False
            ).latest("created_at")
        except EmailOTP.DoesNotExist:
            return False, "OTP not found"
        
        if record.expires_at < timezone.now():
            return False, "OTP expired"
        
        if record.attempts >= 5:
            return False, "Too many attempts"
        
        if not check_password(otp, record.hashed_otp):
            record.attempts += 1
            record.save()
            return False, "Invalid OTP"
        
        record.is_used = True
        record.save()

        return True, "OTP verified"