import json
import re
from http import HTTPStatus

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.http.response import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status

from post_app.repositories import (PostImagesRepository, PostLikeRepository,
                                   PostsRepository)
from post_app.serializers import PostSerializer
from post_app.services import PostLikeService, PostsService
from user_app.models import Users

from .models import Posts

# Create your views here.


@login_required(login_url="/")
@csrf_exempt
def user_posts(request: HttpRequest, user_id: int) -> HttpResponse:
    if request.method == "GET":
        try:
            user = get_object_or_404(Users, user_id=user_id)
            current_user = PostsRepository.get_user(
                username=request.user.username if isinstance(request.user, AbstractBaseUser) else None)
        except Users.DoesNotExist:
            return JsonResponse(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )

        posts = PostsRepository.posts_filtered(post_order="-created_at", user=user)
        serializer = PostSerializer(posts, many=True)
        return render(
            request,
            "userPosts.html",
            {"posts": serializer.data, "user": user, "current_user": current_user},
        )

    return JsonResponse(
        {"error": "Method is not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED
    )


@login_required(login_url="/")
@csrf_exempt
def user_posts_create(request: HttpRequest, user_id: int) -> HttpResponse:
    user = get_object_or_404(Users, user_id=user_id)

    if request.user.is_authenticated and request.user.username != user.username:
        return redirect("user_posts", user_id=user.user_id)

    if request.method == "GET":
        return render(request, "createPost.html", {"user": user})

    elif request.method == "POST":
        description = request.POST["description"]
        post = PostsRepository.create(user=user, description=description)
        PostsRepository.save(post)

        hashtags = re.findall(r"#(\w+)", description)
        PostsService.add_tags(post, hashtags)

        # Save post images
        images = request.FILES.getlist("images")
        for image in images:
            post_image = PostImagesRepository.get(post=post, image=image)

            PostImagesRepository.save(post_image)

        return redirect(f"/users/{user.user_id}/posts")

    return JsonResponse(
        {"error": "Method is not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED
    )


@login_required(login_url="/")
@csrf_exempt
def user_post_details(
    request: HttpRequest, user_id: int, post_id: int
) -> HttpResponse:
    post = PostsRepository.get(post_id=post_id, user_id=user_id)
    user = PostsRepository.get_user(user_id=user_id)
    active_user = PostsRepository.get_user(
        username=request.user.username if isinstance(request.user, AbstractBaseUser) else None)

    if request.method == "GET":
        post = get_object_or_404(Posts, post_id=post_id, user_id=user_id)
        serializer = PostSerializer(post)
        likes = PostLikeRepository.get_filtered_by_post(post)

        num_likes = likes.count
        liked = PostLikeService.is_liked(likes, active_user)

        return render(
            request,
            "userPost.html",
            {
                "post": serializer.data,
                "user": user,
                "post_liked": liked,
                "post_counter": post,
                "num_likes": num_likes,
                "data": post.created_at_formatted(),
            },
        )

    elif request.method == "POST":
        if request.user.is_authenticated:
            like_post(
                request,
                post=post,
                user_id=user_id,
                post_id=post_id,
                active_user=active_user,
            )
            return redirect("user_post_details", user_id=user_id, post_id=post_id)

    elif request.method == "PATCH":
        data = json.loads(request.body)
        serializer = PostSerializer(post, data=data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=status.HTTP_200_OK)
        else:
            return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "DELETE":
        PostsRepository.delete(post)

        return HttpResponse(status=HTTPStatus.NO_CONTENT)

    return JsonResponse(
        {"error": "Method is not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED
    )


@login_required(login_url="/")
def like_post(
    request: HttpRequest, post, active_user, user_id: int = None, post_id: int = None
) -> HttpResponse:
    PostsService.like_post(post, active_user)

    if post_id or user_id:
        return redirect("user_post_details", user_id=user_id, post_id=post_id)
    else:
        return redirect("home")


@login_required(login_url="/")
@csrf_exempt
def all_posts(request: HttpRequest) -> HttpResponse:
    active_user = PostsRepository.get_user(
        username=request.user.username if isinstance(request.user, AbstractBaseUser) else None)

    if request.method == "GET":

        posts_data = []
        posts = PostsRepository.all_posts(post_order="-created_at")

        for post in posts:
            likes = PostLikeRepository.get_filtered_by_post(post)
            num_likes = likes.count
            liked = PostLikeService.is_liked(likes, active_user)

            post_data = {
                "user_id": post.user.user_id,
                "post_id": post.post_id,
                "username": post.user.username,
                "description": post.description,
                "images": post.images.all,
                "created_at": post.created_at_formatted(),
                "post_liked": liked,
                "num_likes": num_likes,
                "active_user": active_user,
            }
            posts_data.append(post_data)

        return render(
            request,
            "allPosts.html",
            {"posts_data": posts_data, "active_user": active_user},
        )

    elif request.method == "POST":
        post_id = request.POST.get("post_id")

        try:
            post = PostsRepository.get(post_id=post_id)

        except Posts.DoesNotExist:
            return JsonResponse(
                {"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND
            )

        if request.user.is_authenticated:
            like_post(request, post=post, active_user=active_user)
            return redirect("all_posts")

    return JsonResponse(
        {"error": "Method is not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED
    )


@login_required(login_url="/")
@csrf_exempt
def tagged_posts(request: HttpRequest, tag_name) -> HttpResponse:
    active_user = PostsRepository.get_user(
        username=request.user.username if isinstance(request.user, AbstractBaseUser) else None)

    if request.method == "GET":

        posts_data = []
        posts = PostsRepository.posts_filtered(
            post_order="-created_at", tags__name=tag_name
        )

        for post in posts:
            likes = PostLikeRepository.get_filtered_by_post(post)

            num_likes = likes.count
            liked = PostLikeService.is_liked(likes, active_user)

            post_data = {
                "user_id": post.user.user_id,
                "post_id": post.post_id,
                "username": post.user.username,
                "description": post.description,
                "images": post.images.all,
                "created_at": post.created_at_formatted(),
                "post_liked": liked,
                "num_likes": num_likes,
                "active_user": active_user,
            }
            posts_data.append(post_data)

        return render(
            request,
            "allPosts.html",
            {"posts_data": posts_data, "active_user": active_user},
        )

    elif request.method == "POST":
        post_id = request.POST.get("post_id")
        post = PostsRepository.get(post_id=post_id)

        if request.user.is_authenticated:
            like_post(request, post=post, active_user=active_user)
            return HttpResponseRedirect(request.path_info)

    return JsonResponse(
        {"error": "Method is not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED
    )
