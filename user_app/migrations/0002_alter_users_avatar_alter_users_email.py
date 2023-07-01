# Generated by Django 4.0.4 on 2023-03-26 20:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("user_app", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="users",
            name="Avatar",
            field=models.TextField(default="default_avatar"),
        ),
        migrations.AlterField(
            model_name="users",
            name="Email",
            field=models.EmailField(blank=True, max_length=254, unique=True),
        ),
    ]