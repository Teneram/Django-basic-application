from django.urls import path

from UserApp import views

urlpatterns = [
    path("", views.home, name="home"),
    path('logout', views.custom_logout, name='logout'),
    path("registration", views.registration, name="registration"),
    path("users", views.users, name="users_list"),
    path("users/<id>", views.user_profile, name="user_profile"),
    path("users/<id>/edit", views.edit_profile, name="edit_profile"),
    path('activate/<uidb64>/<token>', views.activate, name='activate')
]
