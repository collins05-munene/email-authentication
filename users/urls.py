from django.urls import path
from . import views

urlpatterns = [
    path("request-otp/", views.RequestOTPView.as_view(), name="postman-request-otp"),
    path("verify-otp/", views.VerifyOTPView.as_view(), name="postman-verify-otp"),
    
    path("", views.HomeView.as_view(), name="home"),
    path("auth/request-otp/", views.RequestOTPPageView.as_view(), name="request-otp"),
    path("auth/verify-otp/", views.VerifyOTPPageView.as_view(), name="verify-otp"),
    path("dashboard/", views.DashboardView.as_view(), name="login-success"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("logged-out/", views.LoggedOutView.as_view(), name="logged-out"),
    path("me/", views.me)
]