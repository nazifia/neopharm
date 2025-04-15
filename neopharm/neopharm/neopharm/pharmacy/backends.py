from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

class MobileBackend(ModelBackend):
    def authenticate(self, request, mobile=None, password=None, **kwargs):
        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(mobile=mobile)
        except UserModel.DoesNotExist:
            return None

        if user.check_password(password):
            return user
        return None

    def get_user(self, user_id):
        UserModel = get_user_model()
        try:
            return UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None