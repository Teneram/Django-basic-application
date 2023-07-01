import re

from django.shortcuts import get_object_or_404
from rest_framework import serializers

from post_app.models import PostImages, Posts
from user_app.models import Users


class PostImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostImages
        fields = (
            "post_image_id",
            "image",
        )

    def to_representation(self, instance: PostImages) -> dict:
        """Custom representation of the PostImage object."""
        data = super().to_representation(instance)
        if instance.image:
            data["image"] = instance.image.url
        return data


class PostSerializer(serializers.ModelSerializer):
    images = PostImageSerializer(many=True, required=False)

    class Meta:
        model = Posts
        fields = ("post_id", "created_at", "description", "user", "images")
        read_only_fields = ("post_id", "created_at", "user")

    def validate(self, attrs: dict) -> dict:
        """Custom validation for the PostSerializer."""
        images_data = attrs.get("images")
        if images_data and len(images_data) > 10:
            raise serializers.ValidationError("Cannot upload more than 10 images.")
        return attrs

    def create(self, validated_data: dict) -> dict:
        user_id = self.context.get("user_id")
        user = get_object_or_404(Users, user_id=user_id)
        images_data = validated_data.pop("images", None)
        post = Posts.objects.create(user=user, **validated_data)

        if images_data:
            for image_data in images_data:
                PostImages.objects.create(post=post, **image_data)

        return post.to_dict()

    def update(self, instance: Posts, validated_data: dict) -> Posts:
        """Custom update logic for the PostSerializer."""

        # Update post description
        instance.description = validated_data.get("description", instance.description)

        # Update post tags based on the updated description
        hashtags = re.findall(r"#(\w+)", instance.description)
        instance.tags.set(hashtags)

        instance.save()

        return instance
