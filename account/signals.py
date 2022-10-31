from djoser.signals import user_activated
from django.dispatch import receiver
from account.views import UserViewSet


@receiver(signal=user_activated, sender=UserViewSet)
def verify_email(sender, **kwargs):
    user = kwargs.get('user')
    if user:
        user.is_email_verified = True
        user.save()