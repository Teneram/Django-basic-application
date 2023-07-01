from django.urls import path

from user_app import views

urlpatterns = [
    path("", views.home, name="home"),
    path("logout", views.custom_logout, name="logout"),
    path("registration", views.registration, name="registration"),
    path("users", views.users, name="users_list"),
    path("users/<id>", views.user_profile, name="user_profile"),
    path("users/<id>/edit", views.edit_profile, name="edit_profile"),
    path("activate/<uidb64>/<token>", views.activate, name="activate"),
    path("password_change", views.password_change, name="password_change"),
    path("password_reset", views.password_reset_request, name="password_reset"),
    path(
        "reset/<uidb64>/<token>",
        views.passwordResetConfirm,
        name="password_reset_confirm",
    ),
]
