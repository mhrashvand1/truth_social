from djoser.signals import user_activated, user_registered
from django.dispatch import receiver
from account.views import UserViewSet
from account.models import Profile
from activity.models import OnlineStatus

@receiver(signal=user_activated, sender=UserViewSet)
def verify_email(sender, **kwargs):
    user = kwargs.get('user')
    if user:
        user.is_email_verified = True
        user.save()
        
@receiver(signal=user_registered, sender=UserViewSet)      
def create_profile(sender, **kwargs):
    user = kwargs.get('user')
    if user:
        Profile.objects.create(user=user)

@receiver(signal=user_registered, sender=UserViewSet)      
def create_online_status(sender, **kwargs):
    user = kwargs.get('user')
    if user:
        OnlineStatus.objects.create(user=user)