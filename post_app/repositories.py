from django.db.models import QuerySet

from post_app.models import PostImages, PostLike, Posts
from user_app.models import Users


class PostsRepository:
    @staticmethod
    def get(**kwargs) -> Posts:
        return Posts.objects.get(**kwargs)

    @staticmethod
    def save(post: Posts) -> None:
        post.save()

    @staticmethod
    def delete(post: Posts) -> None:
        post.delete()

    @staticmethod
    def create(**kwargs) -> Posts:
        return Posts(**kwargs)

    @staticmethod
    def get_user(**kwargs) -> Users:
        return Users.objects.get(**kwargs)

    @staticmethod
    def posts_filtered(post_order, **post_filter) -> QuerySet[Posts]:
        return Posts.objects.filter(**post_filter).order_by(post_order)

    @staticmethod
    def all_posts(post_order) -> QuerySet[Posts]:
        return Posts.objects.all().order_by(post_order)


class PostImagesRepository:
    @staticmethod
    def get(**kwargs) -> PostImages:
        return PostImages(**kwargs)

    @staticmethod
    def save(post_image) -> None:
        post_image.save()


class PostLikeRepository:
    @staticmethod
    def get(post, user) -> PostLike:
        return PostLike.objects.get(post=post, user=user)

    @staticmethod
    def get_filtered_by_post(post) -> QuerySet[PostLike]:
        return PostLike.objects.filter(post=post)

    @staticmethod
    def add(post, user) -> PostLike:
        return PostLike.objects.create(post=post, user=user)

    @staticmethod
    def save(post_like) -> None:
        post_like.save()

    @staticmethod
    def delete(post_like) -> None:
        post_like.delete()
