from django import forms

class RequestOTPForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            "class": "input",
            "placeholder": "Enter your email"
        })
    )


class VerifyOTPForm(forms.Form):
    otp = forms.CharField(
        max_length=6,
        widget=forms.TextInput(attrs={
            "class": "input",
            "placeholder": " the 6 digit OTP sent to your email"
        })
    )