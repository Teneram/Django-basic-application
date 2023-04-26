from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser

from UserApp.serializers import UserSerializer, UserUpdateSerializer

from .models import Users

from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate, get_user_model
from .forms import SignupForm, UserLoginForm
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from UserApp.tokens import account_activation_token
from django.core.mail import EmailMessage
from django.contrib import messages
from UserApp.decorators import user_not_authenticated
from django.contrib.auth.decorators import login_required

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
                return redirect("users_list")
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
            # create new user object and set attributes
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            # create new Users object and copy relevant data
            user_app = Users.objects.create(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password1']
            )

            # send activation email
            current_site = get_current_site(request)
            mail_subject = 'Activation link has been sent to your email id'
            message = render_to_string('acc_active_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(
                        mail_subject, message, to=[to_email]
            )
            email.send()
            messages.success(request, 'Please confirm your email address to complete the registration')
            return redirect('home')

        else:
            # form is not valid, display error messages
            for field, errors in form.errors.items():
                for error in errors:
                    # messages.error(request, f"{field}: {error}")
                    messages.error(request, f"Error: {error}")
    else:
        form = SignupForm()
    return render(request, 'registration.html', {'form': form})


def activate(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
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

        # Retrieve the search query from the URL query parameters
        search_query = request.GET.get('search')

        # Query the database to filter users based on the search query
        if search_query:
            users_all = Users.objects.filter(username__icontains=search_query)
        else:
            users_all = Users.objects.all()

        # users_all = Users.objects.all()
        current_user = Users.objects.get(username=request.user.username)
        users_serializer = UserSerializer(users_all, many=True)

        return render(request, "users.html", {"users": users_serializer.data, "current_user": current_user})


@login_required
def custom_logout(request):
    logout(request)
    messages.info(request, "Logged out successfully!")
    return redirect("home")


@login_required(login_url='/')
@csrf_exempt
@api_view(["GET", "PATCH", "DELETE"])
@parser_classes([MultiPartParser])
def user_profile(request, id):
    try:
        user = Users.objects.get(user_id=id)
    except Users.DoesNotExist:
        return JsonResponse(
            {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
        )

    if request.method == "GET":
        user_serializer = UserSerializer(user)
        return render(request, "userProfile.html", {"user": user_serializer.data})

    elif request.method == "DELETE":
        User = get_user_model()
        try:
            auth_user = User.objects.get(username=user.username)
        except User.DoesNotExist:
            auth_user = None

        user.delete()
        if auth_user:
            auth_user.delete()

        return JsonResponse(
            {"message": "Deleted successfully"}, status=status.HTTP_204_NO_CONTENT
        )


@login_required(login_url='/')
@csrf_exempt
@api_view(["GET", "PATCH"])
@parser_classes([MultiPartParser])
def edit_profile(request, id):
    try:
        user = Users.objects.get(user_id=id)
    except Users.DoesNotExist:
        return JsonResponse(
            {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
        )

    if request.user.username != user.username:
        return redirect('user_profile', id=user.user_id)

    if request.method == "GET":
        user_serializer = UserSerializer(user)
        return render(request, "editProfile.html", {"user": user_serializer.data})

    elif request.method == "PATCH":
        data = request.data
        avatar = request.FILES.get("avatar")
        user_serializer = UserUpdateSerializer(user, data=data)

        if user_serializer.is_valid():
            user_serializer.save()
            if avatar:
                user.avatar = avatar
                user.save()
            return JsonResponse({"success": True})

        else:
            return JsonResponse(
                user_serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )
