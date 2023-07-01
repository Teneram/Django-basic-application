from typing import List, Optional

from django.db.models.query import QuerySet
from taggit.models import Tag

from post_app.models import PostLike, Posts
from post_app.repositories import PostLikeRepository
from user_app.models import Users


class PostsService:
    @staticmethod
    def add_tags(post: Posts, hashtags: List[str]) -> None:
        for tag_name in hashtags:
            tag, created = Tag.objects.get_or_create(name=tag_name)
            post.tags.add(tag)

    @staticmethod
    def like_post(post: Posts, user: Users) -> None:
        try:
            post_like = PostLikeRepository.get(post, user)
            PostLikeRepository.delete(post_like)
        except PostLike.DoesNotExist:
            post_like = PostLikeRepository.add(post, user)
            PostLikeRepository.save(post_like)


class PostLikeService:
    @staticmethod
    def is_liked(likes: QuerySet[PostLike], user: Optional[Users]) -> bool:
        return likes.filter(user=user).exists()
