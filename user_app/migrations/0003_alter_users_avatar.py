# Generated by Django 4.0.4 on 2023-03-30 19:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("user_app", "0002_alter_users_avatar_alter_users_email"),
    ]

    operations = [
        migrations.AlterField(
            model_name="users",
            name="Avatar",
            field=models.ImageField(
                default="profile_images/default_avatar.png", upload_to="profile_images"
            ),
        ),
    ]
