from typing import Optional

from django.contrib import messages
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.core.files.uploadedfile import UploadedFile
from django.core.mail import EmailMessage
from django.http import HttpRequest, HttpResponse
from django.http.response import JsonResponse
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from user_app.forms import SignupForm
from user_app.models import Users
from user_app.repositories import UsersRepository
from user_app.serializers import UserUpdateSerializer
from user_app.tokens import account_activation_token


class UsersService:
    @staticmethod
    def update_user(
        request: HttpRequest,
        user: Users,
        data: dict,
        avatar: Optional[UploadedFile],
    ) -> HttpResponse | None:
        user_serializer = UserUpdateSerializer(request.user, data=data)
        users_serializer = UserUpdateSerializer(user, data=data)

        if user_serializer.is_valid() and users_serializer.is_valid():
            user_serializer.save()
            users_serializer.save()

            UsersRepository.update(user=user, avatar=avatar)

        else:
            for key, error_list in user_serializer.errors.items():
                for error in error_list:
                    messages.error(request, f"Error: {error}")
                    return JsonResponse({"success": False})

        return None

    @staticmethod
    def register_user(username: str, email: str, password: str) -> Users:
        user = UsersRepository.create_user(
            username=username, email=email, password=password
        )
        return user

    @staticmethod
    def send_activation_email(
        request: HttpRequest, user: User, form: SignupForm
    ) -> None:
        current_site = get_current_site(request)
        mail_subject = "Activation link has been sent to your email id"
        message = render_to_string(
            "acc_active_email.html",
            {
                "user": user,
                "domain": current_site.domain,
                "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                "token": account_activation_token.make_token(user),
            },
        )
        to_email = form.cleaned_data.get("email")
        email = EmailMessage(mail_subject, message, to=[to_email])
        email.send()

    @staticmethod
    def get_auth_user_by_username(username: str) -> Optional[AbstractBaseUser]:
        return UsersRepository.get_user_auth(username=username)

    @staticmethod
    def reset_password_massage(request: HttpRequest, user: AbstractBaseUser) -> str:
        message = render_to_string(
            "template_reset_password.html",
            {
                "user": user,
                "domain": get_current_site(request).domain,
                "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                "token": account_activation_token.make_token(user),
                "protocol": "https" if request.is_secure() else "http",
            },
        )
        return message

    @staticmethod
    def reset_password(request: HttpRequest, user_email: str) -> None:
        associated_user = UsersRepository.get_associated_user(user_email)

        if associated_user:
            subject = "Password Reset request"
            message = UsersService.reset_password_massage(request, associated_user)

            email = EmailMessage(subject, message, to=[associated_user.email])
            if email.send():
                messages.success(
                    request,
                    """
                    <h2>Password reset sent. </h2><hr>
                    <p>
                        We've emailed you instructions for setting your password, if an account exists with the email you entered.
                        You should receive them shortly.<br> If you don't receive an email, please make sure you've entered the address
                        you registered with, and check your spam folder.
                    </p>
                    """,  # noqa
                )
            else:
                messages.error(
                    request,
                    "Problem sending reset password email, <b>SERVER PROBLEM</b>",
                )
