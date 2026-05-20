import json
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render

from .services.otp_service import OTPService
from .services.email_service import EmailService
from .services.auth_service import AuthService

# Create your views here.
def normalize_email(email):
    return email.strip().lower()


@method_decorator(csrf_exempt, name="dispatch")
class RequestOTPView(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            email = normalize_email(data.get("email", ""))

            if not email:
                return JsonResponse({"error": "Email is required"}, status=400)
            
            otp, _ = OTPService.create_otp_record(email)

            EmailService.send_otp(email, otp)

            return JsonResponse({"message": "OTP sent successfully"}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
        

@method_decorator(csrf_exempt, name="dispatch")
class VerifyOTPView(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            email = normalize_email(data.get("email", ""))
            otp = data.get("otp", "")

            if not email or not otp:
                return JsonResponse({"error": "Email and required"}, status=400)
            
            valid, message = OTPService.verify_otp(email, otp)

            if not valid:
                return JsonResponse({"error": message}, status=400)
            
            user = AuthService.get_or_create_user(email)
            AuthService.login_user(request, user)

            return JsonResponse({
                "message": "Authentication successful",
                "user": {
                    "id": str(user.id),
                    "email": user.email
                }
            }, status = 200)
        
        except Exception:
            return JsonResponse({
                "error": "Server error"
            }, status=500)


""" Login debugger"""
def me(request):
    return JsonResponse(
        {
            "authenticated": request.user.is_authenticated,
            "email": request.user.email if request.user.is_authenticated else None
        }
    )