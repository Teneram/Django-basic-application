import datetime
import os
import random

import factory.fuzzy
import pytz
from django.core.files import File
from factory import Faker
from faker import Faker
from PIL import Image

from djangogramm import settings

from .models import PostImages


class PostFactory(factory.django.DjangoModelFactory):
    created_at = factory.fuzzy.FuzzyDateTime(
        start_dt=datetime.datetime(2023, 1, 1, 0, 0, tzinfo=pytz.UTC)
    )
    description = Faker("en_US").paragraph()
    user = factory.SubFactory("UserApp.factories.UserFactory")

    class Meta:
        model = "PostApp.Posts"

    @factory.post_generation
    def images(self, create, extracted, **kwargs):
        if not create:
            return

        num_images = random.randint(1, 10)
        for i in range(num_images):
            PostImageFactory.create(post=self)


class PostImageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = PostImages

    post = factory.SubFactory(PostFactory)

    @factory.post_generation
    def image(self, create, extracted, **kwargs):
        if not create:
            return

        # Set the path where you want to save the images
        save_path = settings.MEDIA_ROOT

        # Generate a random image filename
        image_name = Faker().file_name(extension="jpg")

        # Generate a random image
        image = Image.new("RGB", (640, 480), color=Faker().hex_color())

        # Save the image to the local folder
        image_path = os.path.join(save_path, image_name)
        image.save(image_path)

        # Set the image field of the PostImage instance to the saved image
        self.image.save(image_name, File(open(image_path, "rb")))
