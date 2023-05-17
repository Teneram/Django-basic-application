from django.contrib.auth import get_user_model
from django.http.response import JsonResponse
from django.db.models.query_utils import Q
from rest_framework import status

from UserApp.models import Users


User = get_user_model()


class UsersRepository:
    model = Users

    @staticmethod
    def update_user(user: Users, avatar=None):
        if avatar:
            user.avatar = avatar
        user.save()

    @staticmethod
    def create_user(username, email, password) -> Users:
        return Users.objects.create(
            username=username,
            email=email,
            password=password
        )

    @staticmethod
    def get_user_auth(user_id=None, username=None) -> Users | None:
        try:
            if user_id:
                return User.objects.get(pk=user_id)
            elif username:
                return User.objects.get(username=username)
        except User.DoesNotExist:
            return None

    @staticmethod
    def get_user(user_id=None, username=None) -> Users | JsonResponse:
        try:
            if user_id:
                return Users.objects.get(user_id=user_id)
            elif username:
                return Users.objects.get(username=username)

        except Users.DoesNotExist:
            return JsonResponse(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )

    @staticmethod
    def get_users(search_query) -> Users:
        if search_query:
            return Users.objects.filter(username__icontains=search_query)
        else:
            return Users.objects.all()

    @staticmethod
    def delete_user(user, auth_user=None) -> None:
        user.delete()
        if auth_user:
            auth_user.delete()

    @staticmethod
    def get_associated_user(user_email):
        return get_user_model().objects.filter(Q(email=user_email)).first()
