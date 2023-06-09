import random

from factory import RelatedFactoryList, sequence
from factory.django import DjangoModelFactory
from factory.faker import Faker

from post_app.factories import PostFactory
from user_app.models import Users


class UserFactory(DjangoModelFactory):
    email = Faker("email")
    password = "secret"
    posts = RelatedFactoryList(PostFactory, "user", size=lambda: random.randint(1, 5))
    is_registered = True
    biography = Faker("paragraph")

    @sequence
    def username(n):
        try:
            max_id = Users.objects.latest("user_id").user_id
            return f"User-{max_id + 1}"

        except Users.DoesNotExist:
            return "User-0"

    class Meta:
        model = "user_app.Users"
        django_get_or_create = ["username"]
