from django.dispatch import receiver
from activity import signals
from activity.views import BlockViewSet, FollowViewSet
from notification.models import Notification, Bell
from django.db.models import Q
from notification.constants import FOLLOW_MESSAGE, FOLLOW_PRIORITY, NOTIF_TYPES
from common.utils import get_reverse_dict


@receiver(signal=signals.follow_user, sender=FollowViewSet)
def create_follow_notification(sender, **kwargs):
    current_user = kwargs['current_user']
    target_user = kwargs['target_user']
    Notification.objects.create(
        to=target_user,
        notif_type=get_reverse_dict(dict(NOTIF_TYPES))['follow'],
        priority=FOLLOW_PRIORITY,
        message=FOLLOW_MESSAGE.format(current_user.username),
        has_read=False
    )

@receiver(signal=signals.unfollow_user, sender=FollowViewSet)
def delete_bell_after_unfollow(sender, **kwargs):
    current_user = kwargs['current_user']
    target_user = kwargs['target_user']
    qs = Bell.objects.filter(from_user=current_user, to_user=target_user)
    qs.delete()
  
    
@receiver(signal=signals.block_user, sender=BlockViewSet)
def delete_bells_after_block(sender, **kwargs):
    current_user = kwargs['current_user']
    target_user = kwargs['target_user']
    queryset = Bell.objects.filter(
        Q(from_user=current_user, to_user=target_user) | 
        Q(from_user=target_user, to_user=current_user)
    )
    queryset.delete()