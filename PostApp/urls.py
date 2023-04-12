from django.urls import path

from PostApp import views

urlpatterns = [
    path("users/<user_id>/posts", views.user_posts, name="user_posts"),
    path("users/<user_id>/posts/create", views.user_posts_create, name="create_post"),
    path(
        "users/<user_id>/posts/<post_id>",
        views.user_post_details,
        name="user_post_details",
    ),
]