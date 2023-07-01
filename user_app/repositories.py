from typing import Optional

from django.contrib.auth import get_user_model
from django.contrib.auth.base_user import AbstractBaseUser
# from django.db.models import FileDescriptor
from django.db.models.query import QuerySet
from django.db.models.query_utils import Q

from user_app.models import Users

User = get_user_model()


class UsersRepository:
    model = Users

    @staticmethod
    def update(user: Users, avatar) -> None:
        if avatar:
            user.avatar = avatar
        user.save()

    @staticmethod
    def create_user(username: str, email: str, password: str) -> Users:
        return Users.objects.create(username=username, email=email, password=password)

    @staticmethod
    def get_user_auth(**kwargs) -> AbstractBaseUser | None:
        try:
            return User.objects.get(**kwargs)
        except User.DoesNotExist:
            return None

    @staticmethod
    def get_user(**kwargs) -> Users:
        return Users.objects.get(**kwargs)

    @staticmethod
    def get_users(search_query: Optional[str]) -> QuerySet[Users]:
        if search_query:
            return Users.objects.filter(username__icontains=search_query)
        else:
            return Users.objects.all()

    @staticmethod
    def delete_user(user: Users) -> None:
        auth_user = UsersRepository.get_user_auth(username=user.username)
        user.delete()
        if auth_user:
            auth_user.delete()

    @staticmethod
    def get_associated_user(user_email: str) -> Optional[AbstractBaseUser]:
        return get_user_model().objects.filter(Q(email=user_email)).first()
