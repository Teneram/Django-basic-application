from django.apps import AppConfig


class UserappConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "UserApp"

    def ready(self):
        import UserApp.signals
