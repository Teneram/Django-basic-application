from django.urls import path

from UserApp import views

urlpatterns = [
    path("", views.home, name="home"),
    path("registration", views.registration, name="registration"),
    path("users", views.users, name="users_list"),
    path("users/<id>", views.user_profile, name="user_profile"),
    path("users/<id>/edit", views.edit_profile, name="edit_profile"),
]
