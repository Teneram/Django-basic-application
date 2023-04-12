import random

from django.core.management.base import BaseCommand
from halo import Halo

from PostApp.factories import PostFactory
from UserApp.factories import UserFactory


class Command(BaseCommand):
    help = "Generate fake data and seed the models with them, default are 10"

    def add_arguments(self, parser):
        parser.add_argument(
            "--amount", type=int, help="The amount of the fake data you want"
        )

    def _generate_users(self, amount: int):
        return UserFactory.create_batch(amount)

    @Halo(text="Generating...", spinner="dots", color="blue", text_color="blue")
    def handle(self, *args, **options):
        amount = options.get("amount") or 10
        users = self._generate_users(amount)

        for user in users:
            num_posts = min(random.randint(1, 10), 10)
            PostFactory.create_batch(num_posts, user=user)
