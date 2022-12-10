from django.core.management.base import BaseCommand
from account.models import User, Profile
from activity.models import OnlineStatus

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='username')
        parser.add_argument('password', type=str, help='password')

    def handle(self, *args, **kwargs):
        username = kwargs.get("username")
        password = kwargs.get("password")
        
        try:
            user = User.objects.create_user(
                username=username, 
                password=password,
                email=f"{username}@mail.com",
                name=username
            )
            Profile.objects.create(user=user)
            OnlineStatus.objects.create(user=user)
            self.stdout.write(
                self.style.SUCCESS(f'User {username} created successfully.')
            )
        except:
            self.stdout.write(
                self.style.ERROR('Error while creating user.')
            )