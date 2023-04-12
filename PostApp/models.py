from django.db import models

from UserApp.models import Users

# Create your models here.


class Posts(models.Model):
    post_id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField()
    user = models.ForeignKey(Users, on_delete=models.CASCADE)

    objects = models.Manager()

    def to_dict(self):
        post_dict = {
            "post_id": self.post_id,
            "created_at": self.created_at,
            "description": self.description,
            "user_id": self.user.user_id,
            "user_username": self.user.username,
        }
        first_image = self.images.first()  # first related PostImage object
        if first_image:
            post_dict["image"] = first_image.image
        return post_dict


class PostImages(models.Model):
    post_image_id = models.AutoField(primary_key=True)  # maybe I do not need this line
    image = models.ImageField()
    post = models.ForeignKey(Posts, on_delete=models.CASCADE, related_name="images")

    objects = models.Manager()

    def to_dict(self):
        return {"image": self.image}
