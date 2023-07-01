import random
from typing import List

from django.core.management.base import BaseCommand
from halo import Halo

from post_app.factories import PostFactory
from user_app.factories import UserFactory
from user_app.models import Users


class Command(BaseCommand):
    help = "Generate fake data and seed the models with them, default are 10"

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--amount", type=int, help="The amount of the fake data you want"
        )

    def _generate_users(self, amount: int) -> List[Users]:
        return UserFactory.create_batch(amount)

    @Halo(text="Generating...", spinner="dots", color="blue", text_color="blue")
    def handle(self, *args, **options) -> None:
        amount = options.get("amount") or 10
        users = self._generate_users(amount)

        for user in users:
            num_posts = min(random.randint(1, 10), 10)
            PostFactory.create_batch(num_posts, user=user)
