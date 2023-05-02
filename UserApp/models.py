from django.db import models

# Create your models here.


class Users(models.Model):
    user_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=500)
    password = models.CharField(max_length=500)
    email = models.EmailField(blank=True, unique=True)
    is_registered = models.BooleanField(default=False)
    avatar = models.ImageField(
        upload_to="profile_images", default="profile_images/default_avatar.png"
    )
    biography = models.TextField()

    objects = models.Manager()
