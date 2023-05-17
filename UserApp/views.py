from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse
from django.http.response import JsonResponse
from django.shortcuts import redirect, render
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser

from UserApp.decorators import user_not_authenticated
from UserApp.serializers import UserSerializer
from UserApp.tokens import account_activation_token

from UserApp.forms import (ChangePasswordForm, CustomSetPasswordForm,
                           PasswordResetForm, SignupForm, UserLoginForm)
from UserApp.services import UsersService

# Create your views here.


@user_not_authenticated
def home(request):
    if request.method == "POST":
        form = UserLoginForm(request=request, data=request.POST)

        if form.is_valid():
            user = authenticate(
                request,
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password"]
            )
            if user is not None:
                login(request, user)
                messages.success(request, f"Hello, {user.username}! You have been logged in")
                return redirect("all_posts")
        else:
            for key, error in list(form.errors.items()):
                messages.error(request, error)
    form = UserLoginForm()

    return render(
        request=request,
        template_name="index.html",
        context={"form": form}
    )


def registration(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            # create new Users object and copy relevant data
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password1']
            user_app = UsersService.register_user(username, email, password)

            # send activation email
            UsersService.send_activation_email(request=request, user=user, form=form)
            messages.success(request, 'Please confirm your email address to complete the registration')
            return redirect('home')

        else:
            # form is not valid, display error messages
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Error: {error}")
    else:
        form = SignupForm()
    return render(request, 'registration.html', {'form': form})


def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = UsersService.get_auth_user_by_id(uid)
    except (TypeError, ValueError, OverflowError):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Thank you for your email confirmation. Now you can login your account.')
        return redirect('home')
    else:
        return HttpResponse('Activation link is invalid!')


@login_required(login_url='/')
@csrf_exempt
def users(request):
    if request.method == "GET":
        search_query = request.GET.get('search')
        users_all = UsersService.get_all_users(search_query)
        current_user = UsersService.get_user_by_username(request.user.username)
        users_serializer = UserSerializer(users_all, many=True)

        return render(request, "users.html", {"users": users_serializer.data, "current_user": current_user})


@login_required
def custom_logout(request):
    logout(request)
    messages.info(request, "Logged out successfully!")
    return redirect("home")


@login_required(login_url='/')
@csrf_exempt
@api_view(["GET", "DELETE"])
@parser_classes([MultiPartParser])
def user_profile(request, id):
    user = UsersService.get_user_by_id(user_id=id)

    if request.method == "GET":
        user_serializer = UserSerializer(user)
        return render(request, "userProfile.html", {"user": user_serializer.data})

    elif request.method == "DELETE":
        UsersService.delete_user(user)
        return JsonResponse(
            {"message": "Deleted successfully"}, status=status.HTTP_204_NO_CONTENT
        )


@login_required(login_url='/')
@csrf_exempt
@api_view(["GET", "PATCH"])
@parser_classes([MultiPartParser])
def edit_profile(request, id):
    user = UsersService.get_user_by_id(user_id=id)

    if request.user.username != user.username:
        return redirect('user_profile', id=user.user_id)

    if request.method == "GET":
        user_serializer = UserSerializer(user)
        return render(request, "editProfile.html", {"user": user_serializer.data})

    elif request.method == "PATCH":
        data = request.data
        avatar = request.FILES.get("avatar")

        try:
            UsersService.update_user(request, user, data, avatar)
            messages.success(request, 'Profile data was updated')
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


@login_required
def password_change(request):
    user = request.user
    if request.method == 'POST':
        form = ChangePasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your password has been changed")
            return redirect('users_list')
        else:
            for error in list(form.errors.values()):
                messages.error(request, error)

    form = ChangePasswordForm(user)
    return render(request, 'password_change_confirm.html', {'form': form})


@user_not_authenticated
def password_reset_request(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            user_email = form.cleaned_data['email']
            UsersService.reset_password(request, user_email)
            return redirect('users_list')
    form = PasswordResetForm()
    return render(
        request=request,
        template_name="password_reset.html",
        context={"form": form}
        )


def passwordResetConfirm(request, uidb64, token):
    uid = force_str(urlsafe_base64_decode(uidb64))
    user = UsersService.get_auth_user_by_id(uid)

    if user is not None and account_activation_token.check_token(user, token):
        if request.method == 'POST':
            form = CustomSetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Your password has been set. You may go ahead and <b>log in </b> now.")
                return redirect('users_list')
            else:
                for error in list(form.errors.values()):
                    messages.error(request, error)

        form = CustomSetPasswordForm(user)
        return render(request, 'password_reset_confirm.html', {'form': form})
    else:
        messages.error(request, "Link is expired")

    messages.error(request, 'Something went wrong, redirecting back to Homepage')
    return redirect("users_list")


def passwordChangeConfirm(request, uidb64, token):
    uid = force_str(urlsafe_base64_decode(uidb64))
    user = UsersService.get_auth_user_by_id(uid)

    if user is not None and account_activation_token.check_token(user, token):
        if request.method == 'POST':
            form = ChangePasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Your password has been set. You may go ahead and <b>log in </b> now.")
                return redirect('users_list')
            else:
                for error in list(form.errors.values()):
                    messages.error(request, error)

        form = ChangePasswordForm(user)
        return render(request, 'password_change_confirm.html', {'form': form})
    else:
        messages.error(request, "Link is expired")

    messages.error(request, 'Something went wrong, redirecting back to Homepage')
    return redirect("users_list")
