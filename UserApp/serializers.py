from django.core.validators import validate_email
from rest_framework import serializers

from UserApp.models import Users


class UserSerializer(serializers.ModelSerializer):
    is_registered = serializers.BooleanField(default=True, label="is_registered")
    avatar = serializers.ImageField(required=False)

    class Meta:
        model = Users
        fields = (
            "user_id",
            "password",
            "email",
            "is_registered",
            "username",
            "avatar",
            "biography",
        )


class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = (
            "user_id",
            "password",
            "email",
            "is_registered",
            "username",
            "avatar",
            "biography",
        )


class UserUpdateSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=False)
    password = serializers.CharField(required=False)
    email = serializers.EmailField(required=False, validators=[validate_email])
    avatar = serializers.ImageField(required=False)
    biography = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = Users
        fields = [
            "user_id",
            "password",
            "email",
            "is_registered",
            "username",
            "avatar",
            "biography",
        ]
        read_only_fields = ["user_id", "is_registered"]
