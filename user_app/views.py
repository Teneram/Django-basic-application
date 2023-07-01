from typing import Optional

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpRequest, HttpResponse
from django.http.response import JsonResponse
from django.shortcuts import redirect, render
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser

from user_app.decorators import user_not_authenticated
from user_app.forms import (ChangePasswordForm, CustomSetPasswordForm,
                            MyPasswordResetForm, SignupForm, UserLoginForm)
from user_app.models import Users
from user_app.repositories import UsersRepository
from user_app.serializers import UserSerializer
from user_app.services import UsersService
from user_app.tokens import account_activation_token

# Create your views here.


@user_not_authenticated
def home(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = UserLoginForm(request=request, data=request.POST)

        if form.is_valid():
            user = authenticate(
                request,
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password"],
            )
            if user is not None:
                login(request, user)
                messages.success(
                    request, f"Hello, {user.username}! You have been logged in"  # noqa
                )
                return redirect("all_posts")
        else:
            for key, error in list(form.errors.items()):
                messages.error(request, error)
    form = UserLoginForm()

    return render(request=request, template_name="index.html", context={"form": form})


def registration(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            # create new Users object and copy relevant data
            username = form.cleaned_data["username"]
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password1"]
            UsersService.register_user(username, email, password)

            # send activation email
            UsersService.send_activation_email(request=request, user=user, form=form)
            messages.success(
                request,
                "Please confirm your email address to complete the registration",
            )
            return redirect("home")

        else:
            # form is not valid, display error messages
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Error: {error}")
    else:
        form = SignupForm()
    return render(request, "registration.html", {"form": form})


def activate(request: HttpRequest, uidb64: str, token: str) -> HttpResponse:
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = UsersRepository.get_user_auth(pk=uid)
    except (TypeError, ValueError, OverflowError):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(
            request,
            "Thank you for your email confirmation. Now you can login your account.",
        )
        return redirect("home")
    else:
        return HttpResponse("Activation link is invalid!")


@login_required(login_url="/")
@csrf_exempt
def users(request: HttpRequest) -> HttpResponse:
    if request.method == "GET":
        search_query = request.GET.get("search")
        users_all = UsersRepository.get_users(search_query)

        try:
            current_user = UsersRepository.get_user(
                username=request.user.username if isinstance(request.user, AbstractBaseUser) else None)
        except Users.DoesNotExist:
            return JsonResponse(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )

        users_serializer = UserSerializer(users_all, many=True)

        return render(
            request,
            "users.html",
            {"users": users_serializer.data, "current_user": current_user},
        )

    return JsonResponse(
        {"error": "Method is not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED
    )


@login_required
def custom_logout(request: HttpRequest) -> HttpResponse:
    logout(request)
    messages.info(request, "Logged out successfully!")
    return redirect("home")


@login_required(login_url="/")
@csrf_exempt
@api_view(["GET", "DELETE"])
@parser_classes([MultiPartParser])
def user_profile(request: HttpRequest, id: int) -> Optional[HttpResponse]:
    user = UsersRepository.get_user(user_id=id)

    if request.method == "GET":
        user_serializer = UserSerializer(user)
        return render(request, "userProfile.html", {"user": user_serializer.data})

    elif request.method == "DELETE":
        UsersRepository.delete_user(user)
        return JsonResponse(
            {"message": "Deleted successfully"}, status=status.HTTP_204_NO_CONTENT
        )

    return None


@login_required(login_url="/")
@csrf_exempt
@api_view(["GET", "PATCH"])
@parser_classes([MultiPartParser])
def edit_profile(request: HttpRequest, id: int) -> Optional[HttpResponse]:
    user = UsersRepository.get_user(user_id=id)

    if request.user.is_authenticated and request.user.username != user.username:

        return redirect("user_profile", id=user.user_id)

    if request.method == "GET":
        user_serializer = UserSerializer(user)
        return render(request, "editProfile.html", {"user": user_serializer.data})

    elif request.method == "PATCH":
        data = request.data
        avatar = request.FILES.get("avatar")

        try:
            UsersService.update_user(request, user, data, avatar)
            messages.success(request, "Profile data was updated")
            return JsonResponse({"success": True})

        except IntegrityError as e:
            error_message = str(e)
            if "unique constraint" in error_message:
                if "UserApp_users_Email_cc414933_uniq" in error_message:
                    messages.error(request, "This email is already in use.")
                elif "auth_user_username_key" in error_message:
                    messages.error(request, "This username is already in use.")
                else:
                    messages.error(request, "An unknown error occurred.")
            else:
                messages.error(request, "An unknown error occurred.")
            return JsonResponse({"success": False})

    return None


@login_required
def password_change(request: HttpRequest) -> HttpResponse:
    user = request.user
    if request.method == "POST":
        form = ChangePasswordForm(user if user.is_authenticated else None, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your password has been changed")
            return redirect("users_list")
        else:
            for error in list(form.errors.values()):
                messages.error(request, error)

    form = ChangePasswordForm(user if user.is_authenticated else None)
    return render(request, "password_change_confirm.html", {"form": form})


@user_not_authenticated
def password_reset_request(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = MyPasswordResetForm(request.POST)
        if form.is_valid():
            user_email = form.cleaned_data["email"]
            UsersService.reset_password(request, user_email)
            return redirect("users_list")
    form = MyPasswordResetForm()
    return render(
        request=request, template_name="password_reset.html", context={"form": form}
    )


def passwordResetConfirm(request: HttpRequest, uidb64: str, token: str) -> HttpResponse:
    uid = force_str(urlsafe_base64_decode(uidb64))
    user = UsersRepository.get_user_auth(pk=uid)

    if user is not None and account_activation_token.check_token(user, token):
        if request.method == "POST":
            form = CustomSetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(
                    request,
                    "Your password has been set. You may go ahead and <b>log in </b> now.",
                )
                return redirect("users_list")
            else:
                for error in list(form.errors.values()):
                    messages.error(request, error)

        form = CustomSetPasswordForm(user)
        return render(request, "password_reset_confirm.html", {"form": form})
    else:
        messages.error(request, "Link is expired")

    messages.error(request, "Something went wrong, redirecting back to Homepage")
    return redirect("users_list")


def passwordChangeConfirm(
    request: HttpRequest, uidb64: str, token: str
) -> HttpResponse:
    uid = force_str(urlsafe_base64_decode(uidb64))
    user = UsersRepository.get_user_auth(pk=uid)

    if user is not None and account_activation_token.check_token(user, token):
        if request.method == "POST":
            form = ChangePasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(
                    request,
                    "Your password has been set. You may go ahead and <b>log in </b> now.",
                )
                return redirect("users_list")
            else:
                for error in list(form.errors.values()):
                    messages.error(request, error)

        form = ChangePasswordForm(user)
        return render(request, "password_change_confirm.html", {"form": form})
    else:
        messages.error(request, "Link is expired")

    messages.error(request, "Something went wrong, redirecting back to Homepage")
    return redirect("users_list")
