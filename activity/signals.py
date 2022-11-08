from django.dispatch import Signal

# Args: actor, target_user, request
follow_user = Signal()
unfollow_user = Signal()
block_user = Signal()
