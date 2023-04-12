import json
from http import HTTPStatus

from django.http import HttpResponse, HttpResponseRedirect
from django.http.response import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status

from PostApp.serializers import PostSerializer
from UserApp.models import Users

from .models import PostImages, Posts

# Create your views here.


@csrf_exempt
def user_posts(request, user_id):
    if request.method == "GET":
        user = get_object_or_404(Users, user_id=user_id)
        posts = Posts.objects.filter(user=user).order_by("-created_at")
        serializer = PostSerializer(posts, many=True)
        return render(
            request, "userPosts.html", {"posts": serializer.data, "user": user}
        )


@csrf_exempt
def user_posts_create(request, user_id):
    if request.method == "GET":
        return render(request, "createPost.html")

    elif request.method == "POST":
        print("HELLOW")
        user = get_object_or_404(Users, user_id=user_id)
        post = Posts(user=user, description=request.POST["description"])
        post.save()

        # Save post images
        images = request.FILES.getlist("images")
        for image in images:
            post_image = PostImages(post=post, image=image)
            post_image.save()
            print("Image added ")
        return redirect(f"/users/{user.user_id}/posts")


@csrf_exempt
def user_post_details(request, user_id, post_id):
    try:
        post = Posts.objects.get(post_id=post_id, user_id=user_id)
    except Posts.DoesNotExist:
        return JsonResponse(
            {"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND
        )

    if request.method == "GET":
        print("My get method")
        post = get_object_or_404(Posts, post_id=post_id, user_id=user_id)
        serializer = PostSerializer(post)
        return render(request, "userPost.html", {"post": serializer.data})
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
