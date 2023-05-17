import json
import re
from http import HTTPStatus

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.http.response import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status

from PostApp.serializers import PostSerializer
from UserApp.models import Users

from .models import Posts

from PostApp.services import PostsService, PostImagesService, PostLikeService

# Create your views here.


@login_required(login_url='/')
@csrf_exempt
def user_posts(request, user_id):
    if request.method == "GET":
        user = get_object_or_404(Users, user_id=user_id)
        current_user = PostsService.get_user_by_username(username=request.user.username)
        posts = PostsService.get_filtered_posts(post_order="-created_at", user=user)
        serializer = PostSerializer(posts, many=True)
        return render(
            request, "userPosts.html", {"posts": serializer.data, "user": user, "current_user": current_user}
        )


@login_required(login_url='/')
@csrf_exempt
def user_posts_create(request, user_id):
    user = get_object_or_404(Users, user_id=user_id)

    if request.user.username != user.username:
        return redirect('user_posts', user_id=user.user_id)

    if request.method == "GET":
        return render(request, "createPost.html", {"user": user})

    elif request.method == "POST":
        description = request.POST["description"]
        post = PostsService.create_user_post(user=user, description=description)
        PostsService.save_post(post)

        hashtags = re.findall(r'#(\w+)', description)
        PostsService.add_tags(post, hashtags)

        # Save post images
        images = request.FILES.getlist("images")
        for image in images:
            post_image = PostImagesService.get_image(post, image)
            PostImagesService.save_image(post_image)

        return redirect(f"/users/{user.user_id}/posts")


@login_required(login_url='/')
@csrf_exempt
def user_post_details(request, user_id, post_id):
    post = PostsService.get_post(post_id, user_id)
    user = PostsService.get_user_by_id(user_id)
    active_user = PostsService.get_user_by_username(request.user.username)

    if request.method == "GET":
        post = get_object_or_404(Posts, post_id=post_id, user_id=user_id)
        serializer = PostSerializer(post)

        likes = PostLikeService.get_post_likes(post)
        num_likes = likes.count()
        liked = PostLikeService.is_liked(likes, active_user)

        return render(request, "userPost.html", {
            "post": serializer.data,
            "user": user,
            "post_liked": liked,
            "post_counter": post,
            "num_likes": num_likes,
            "data": post.created_at_formatted(),
        })

    elif request.method == "POST":
        if request.user.is_authenticated:
            like_post(request, post=post, user_id=user_id, post_id=post_id, active_user=active_user)
            return redirect('user_post_details', user_id=user_id, post_id=post_id)

    elif request.method == "PATCH":
        data = json.loads(request.body)
        serializer = PostSerializer(post, data=data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=status.HTTP_200_OK)
        else:
            return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "DELETE":
        PostsService.delete_post(post)
        return HttpResponse(status=HTTPStatus.NO_CONTENT)


@login_required(login_url='/')
def like_post(request, post, active_user, user_id=None, post_id=None):
    PostsService.like_post(post, active_user)

    if post_id or user_id:
        return redirect('user_post_details', user_id=user_id, post_id=post_id)
    else:
        return redirect('home')


@login_required(login_url='/')
@csrf_exempt
def all_posts(request):
    active_user = PostsService.get_user_by_username(request.user.username)

    if request.method == "GET":

        posts_data = []
        posts = PostsService.get_all_posts(post_order="-created_at")

        for post in posts:
            likes = PostLikeService.get_post_likes(post)
            num_likes = likes.count()
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
                "active_user": active_user
            }
            posts_data.append(post_data)

        return render(request, "allPosts.html", {"posts_data": posts_data, "active_user": active_user})

    elif request.method == "POST":
        post_id = request.POST.get('post_id')
        post = PostsService.get_post(post_id=post_id)

        if request.user.is_authenticated:
            like_post(request, post=post, active_user=active_user)
            return redirect('all_posts')


@login_required(login_url='/')
@csrf_exempt
def tagged_posts(request, tag_name):
    active_user = PostsService.get_user_by_username(request.user.username)

    if request.method == "GET":

        posts_data = []
        posts = PostsService.get_filtered_posts(post_order="-created_at", tags__name=tag_name)

        for post in posts:
            likes = PostLikeService.get_post_likes(post)
            num_likes = likes.count()
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
                "active_user": active_user
            }
            posts_data.append(post_data)

        return render(request, "allPosts.html", {"posts_data": posts_data, "active_user": active_user})

    elif request.method == "POST":
        post_id = request.POST.get('post_id')
        post = PostsService.get_post(post_id=post_id)
        if request.user.is_authenticated:
            like_post(request, post=post, active_user=active_user)
            return HttpResponseRedirect(request.path_info)
