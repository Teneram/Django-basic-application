from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Users


@receiver(post_save, sender=Users)
def set_user_registered(sender, instance: Users, created: bool, **kwargs):
    if created:
        instance.is_registered = True
        instance.save()
