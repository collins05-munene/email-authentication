import json
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect, render
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout

from .forms import RequestOTPForm, VerifyOTPForm
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

class HomeView(TemplateView):
    template_name = "home.html"


class RequestOTPPageView(View):
    template_name = "auth/request_otp.html"

    def get(self, request):
        form = RequestOTPForm()
        context = {"form": form}
        return render(request, self.template_name, context)
    

    def post(self, request):
        form = RequestOTPForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data["email"].strip().lower()

            otp, _ = OTPService.create_otp_record(email)
            EmailService.send_otp(email, otp)

            request.session["auth_email"] = email

            return redirect("verify-otp")
        
        context = {"form": form}
        return render(request, self.template_name, context)
    
class VerifyOTPPageView(View):
    template_name = "auth/verify_otp.html"

    def get(self, request):
        form = VerifyOTPForm()
        context = {"form": form}
        return render(request, self.template_name, context)
    
    def post(self, request):
        form = VerifyOTPForm(request.POST)

        email = request.session.get("auth_email")

        if not email:
            return redirect("request-otp")
        
        if form.is_valid():
            otp = form.cleaned_data["otp"]

            valid, message = OTPService.verify_otp(email, otp)
            if valid:
                user = AuthService.get_or_create_user(email)
                AuthService.login_user(request, user)
                request.session.pop("auth_email", None)
                return redirect("login-success")
            
            form.add_error("otp", message)

            context = {"form": form}
            return render(request, self.template_name, context)
        

@method_decorator(login_required, name="dispatch")
class DashboardView(TemplateView):
    template_name = "auth/success.html"


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect("logged-out")
    

class LoggedOutView(TemplateView):
    template_name = "auth/logged_out.html"