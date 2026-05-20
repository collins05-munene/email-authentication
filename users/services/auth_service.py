from django.contrib.auth import get_user_model, login

User = get_user_model()

class AuthService:

    @staticmethod
    def get_or_create_user(email):
        user, created_at = User.objects.get_or_create(
            email=email, defaults={"is_verified": True}
        )
        return user
    
    @staticmethod
    def login_user(request, user):
        login(request, user)