import json
import re
from http import HTTPStatus

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.http.response import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from taggit.models import Tag

from PostApp.serializers import PostSerializer
from UserApp.models import Users

from .models import PostImages, PostLike, Posts

# Create your views here.


@login_required(login_url='/')
@csrf_exempt
def user_posts(request, user_id):
    if request.method == "GET":
        current_user = Users.objects.get(username=request.user.username)
        user = get_object_or_404(Users, user_id=user_id)
        posts = Posts.objects.filter(user=user).order_by("-created_at")
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
        post = Posts(user=user, description=description)
        post.save()

        hashtags = re.findall(r'#(\w+)', description)

        for tag_name in hashtags:
            tag, created = Tag.objects.get_or_create(name=tag_name)
            post.tags.add(tag)

        # Save post images
        images = request.FILES.getlist("images")
        for image in images:
            post_image = PostImages(post=post, image=image)
            post_image.save()
        return redirect(f"/users/{user.user_id}/posts")


@login_required(login_url='/')
@csrf_exempt
def user_post_details(request, user_id, post_id):
    try:
        post = Posts.objects.get(post_id=post_id, user_id=user_id)
        user = Users.objects.get(user_id=user_id)
    except Posts.DoesNotExist:
        return JsonResponse(
            {"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND
        )
    active_user = Users.objects.get(username=request.user.username)

    if request.method == "GET":
        post = get_object_or_404(Posts, post_id=post_id, user_id=user_id)
        serializer = PostSerializer(post)

        likes = PostLike.objects.filter(post=post)
        num_likes = likes.count()
        liked = likes.filter(user=active_user).exists()

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
        post.delete()
        return HttpResponse(status=HTTPStatus.NO_CONTENT)


@login_required(login_url='/')
def like_post(request, post, active_user, user_id=None, post_id=None):
    try:
        post_like = PostLike.objects.get(post=post, user=active_user)
        post_like.delete()
    except PostLike.DoesNotExist:
        post_like = PostLike.objects.create(post=post, user=active_user)
        post_like.save()

    if post_id or user_id:
        return redirect('user_post_details', user_id=user_id, post_id=post_id)
    else:
        return redirect('home')


@login_required(login_url='/')
@csrf_exempt
def all_posts(request):
    active_user = Users.objects.get(username=request.user.username)

    if request.method == "GET":

        posts_data = []
        posts = Posts.objects.all().order_by("-created_at")

        for post in posts:
            likes = PostLike.objects.filter(post=post)
            num_likes = likes.count()
            liked = likes.filter(user=active_user).exists()

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
        post = Posts.objects.get(post_id=post_id)
        if request.user.is_authenticated:
            like_post(request, post=post, active_user=active_user)
            return redirect('all_posts')


@login_required(login_url='/')
@csrf_exempt
def tagged_posts(request, tag_name):
    active_user = Users.objects.get(username=request.user.username)

    if request.method == "GET":

        posts_data = []
        posts = Posts.objects.filter(tags__name=tag_name).order_by("-created_at")

        for post in posts:
            likes = PostLike.objects.filter(post=post)
            num_likes = likes.count()
            liked = likes.filter(user=active_user).exists()

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
        post = Posts.objects.get(post_id=post_id)
        if request.user.is_authenticated:
            like_post(request, post=post, active_user=active_user)
            return HttpResponseRedirect(request.path_info)
