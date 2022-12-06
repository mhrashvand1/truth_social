# Generated by Django 4.1.2 on 2022-11-24 17:38

import account.utils
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0004_remove_user_blocked_users_user_bell_enablings_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='avatar',
            field=models.ImageField(blank=True, default='truth_social_media/no_avatar.png', upload_to=account.utils.get_avatar_path, verbose_name='avatar'),
        ),
    ]