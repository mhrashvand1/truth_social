# Generated by Django 4.1.2 on 2022-12-10 14:41

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='updated at')),
                ('notif_type', models.IntegerField(choices=[(0, 'truth_social'), (1, 'follow'), (2, 'like'), (3, 'mention'), (4, 'retweet'), (5, 'new_tweet')], verbose_name='notification type')),
                ('message', models.CharField(max_length=300, verbose_name='message')),
                ('priority', models.IntegerField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')], verbose_name='priority')),
                ('has_read', models.BooleanField(default=False, verbose_name='has read')),
                ('to', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to=settings.AUTH_USER_MODEL, verbose_name='to user')),
            ],
            options={
                'verbose_name': 'notification',
                'verbose_name_plural': 'notifications',
                'db_table': 'Notification',
            },
        ),
        migrations.CreateModel(
            name='Bell',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='updated at')),
                ('priority', models.IntegerField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')], verbose_name='priority')),
                ('from_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bells_from', to=settings.AUTH_USER_MODEL, verbose_name='from user')),
                ('to_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bells_to', to=settings.AUTH_USER_MODEL, verbose_name='to user')),
            ],
            options={
                'verbose_name': 'bell',
                'verbose_name_plural': 'bells',
                'db_table': 'Bell',
                'unique_together': {('from_user', 'to_user')},
            },
        ),
    ]
