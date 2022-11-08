from django.dispatch import receiver
from activity import signals
from activity.views import BlockViewSet
from activity.models import Follow
from django.db.models import Q


@receiver(signal=signals.block_user, sender=BlockViewSet)
def delete_follows_after_block(sender, **kwargs):
    current_user = kwargs['current_user']
    target_user = kwargs['target_user']
    queryset = Follow.objects.filter(
        Q(from_user=current_user, to_user=target_user) | 
        Q(from_user=target_user, to_user=current_user)
    )
    queryset.delete()