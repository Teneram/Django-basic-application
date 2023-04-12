from django.http.response import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser

from UserApp.serializers import UserSerializer, UserUpdateSerializer

from .models import Users

# Create your views here.


def home(request):
    return render(request, "index.html")


def registration(request):
    if request.method == "GET":
        return render(request, "registration.html")

    elif request.method == "POST":
        data = request.POST
        user_serializer = UserUpdateSerializer(data=data)
        if user_serializer.is_valid():
            user = user_serializer.save()
            return redirect(f"/users/{user.user_id}")
        return JsonResponse(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
def users(request):
    if request.method == "GET":
        users_all = Users.objects.all()
        users_serializer = UserSerializer(users_all, many=True)
        return render(request, "users.html", {"users": users_serializer.data})

    elif request.method == "POST":
        data = request.POST
        user_serializer = UserUpdateSerializer(data=data)
        if user_serializer.is_valid():
            user = user_serializer.save()
            return redirect(f"/users/{user.user_id}")

        return JsonResponse(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
        user.delete()
        return JsonResponse(
            {"message": "Deleted successfully"}, status=status.HTTP_204_NO_CONTENT
        )


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

    if request.method == "GET":
        print(" YOU ARE IN GET ")
        user_serializer = UserSerializer(user)
        return render(request, "editProfile.html", {"user": user_serializer.data})

    elif request.method == "PATCH":
        print(" YOU ARE IN PATCH ")
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
