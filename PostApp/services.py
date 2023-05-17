from typing import List

from taggit.models import Tag

from PostApp.repositories import PostsRepository, PostImagesRepository, PostLikeRepository
from PostApp.models import Posts, PostLike, PostImages


class PostsService:

    @staticmethod
    def get_post(post_id, user_id=None):
        if user_id:
            return PostsRepository.get(post_id, user_id)
        else:
            return PostsRepository.get(post_id)

    @staticmethod
    def save_post(post: Posts) -> None:
        PostsRepository.save(post)

    @staticmethod
    def delete_post(post: Posts) -> None:
        PostsRepository.delete(post)

    @staticmethod
    def get_user_by_id(user_id):
        return PostsRepository.get_user(user_id=user_id)

    @staticmethod
    def get_user_by_username(username):
        return PostsRepository.get_user(username=username)

    @staticmethod
    def get_filtered_posts(post_order, **post_filter):
        return PostsRepository.posts_filtered(post_order, **post_filter)

    @staticmethod
    def get_all_posts(post_order):
        return PostsRepository.all_posts(post_order)

    @staticmethod
    def create_user_post(user, description) -> Posts:
        return PostsRepository.create(user, description)

    @staticmethod
    def add_tags(post: Posts, hashtags: List[str]) -> None:
        for tag_name in hashtags:
            tag, created = Tag.objects.get_or_create(name=tag_name)
            post.tags.add(tag)

    @staticmethod
    def like_post(post, user):
        try:
            post_like = PostLikeRepository.get(post, user)
            PostLikeRepository.delete(post_like)
        except PostLike.DoesNotExist:
            post_like = PostLikeRepository.add(post, user)
            PostLikeRepository.save(post_like)


class PostImagesService:

    @staticmethod
    def get_image(post: Posts, image) -> PostImages:
        return PostImagesRepository.get(post, image)

    @staticmethod
    def save_image(post_image) -> None:
        PostImagesRepository.save(post_image)


class PostLikeService:

    @staticmethod
    def get_post_likes(post):
        return PostLikeRepository.get_filtered_by_post(post)

    @staticmethod
    def is_liked(likes, user) -> bool:
        return likes.filter(user=user).exists()
