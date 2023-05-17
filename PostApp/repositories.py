from django.http.response import JsonResponse
from rest_framework import status

from PostApp.models import Posts, PostImages, PostLike
from UserApp.models import Users


class PostsRepository:

    @staticmethod
    def get(post_id, user_id=None) -> Posts | JsonResponse:
        try:
            if user_id:
                return Posts.objects.get(post_id=post_id, user_id=user_id)
            else:
                return Posts.objects.get(post_id=post_id)
        except Posts.DoesNotExist:
            return JsonResponse(
                {"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND
            )

    @staticmethod
    def save(post: Posts) -> None:
        post.save()

    @staticmethod
    def delete(post: Posts) -> None:
        post.delete()

    @staticmethod
    def create(user: Users, description) -> Posts:
        return Posts(user=user, description=description)

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
    def posts_filtered(post_order, **post_filter):
        return Posts.objects.filter(**post_filter).order_by(post_order)

    @staticmethod
    def all_posts(post_order):
        return Posts.objects.all().order_by(post_order)


class PostImagesRepository:

    @staticmethod
    def get(post: Posts, image) -> PostImages:
        return PostImages(post=post, image=image)

    @staticmethod
    def save(post_image) -> None:
        post_image.save()


class PostLikeRepository:

    @staticmethod
    def get(post, user):
        return PostLike.objects.get(post=post, user=user)

    @staticmethod
    def get_filtered_by_post(post):
        return PostLike.objects.filter(post=post)

    @staticmethod
    def add(post, user):
        return PostLike.objects.create(post=post, user=user)

    @staticmethod
    def save(post_like):
        post_like.save()

    @staticmethod
    def delete(post_like):
        post_like.delete()





