from django.db import models
from django.contrib.auth import get_user_model
from common.models import BaseModel
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class Room(BaseModel):
    
    TYPES = [
        (0, 'private'),
        (1, 'group')
    ]
    room_type = models.IntegerField(
        verbose_name='room type',
        choices=TYPES
    )
    members = models.ManyToManyField(
        to=User, 
        related_name='rooms',
        through='RoomUser',
        verbose_name='members',     
    )
    
    def clean(self, *args, **kwargs):
        if self.room_type == 0:
            if self.members.count() > 2:
                raise ValidationError(
                    "You can't assign more than two members to private room"
                )
        super().clean(*args, **kwargs)
    
    class Meta:
        db_table = 'Room'
        verbose_name = _('room')
        verbose_name_plural = _('rooms')
               
# class GroupSpecification(BaseModel):
#     room = models.OneToOneField(
#         to='Room', primary_key=True, db_index=True,
#         on_delete=models.CASCADE, related_name='group_specification',
#         verbose_name='room'
#     )
#     # TODO: implement group chat
#     # group_name
#     # group_avatar
#     # group_bio
#     ...
        
class RoomUser(BaseModel):
    
    room = models.ForeignKey(
        to='Room', 
        on_delete=models.CASCADE,
        related_name='room_user_set',      
        verbose_name='room'
    )
    user = models.ForeignKey(
        to=User, 
        on_delete=models.CASCADE,
        related_name='room_user_set',      
        verbose_name='user'
    )
    last_read = models.DateTimeField(
        default=timezone.now,
        verbose_name='last message read time'
    )
    
    class Meta:
        db_table = 'RoomUser'
        verbose_name = _('room_user')
        verbose_name_plural = _('room_user')
        unique_together = ('room', 'user')
        index_together = ('room', 'user')
           
    
class Message(BaseModel):
    author = models.ForeignKey(
        to=User, on_delete=models.CASCADE,
        related_name='messages', verbose_name='author'
    )
    room = models.ForeignKey(
        to='Room', on_delete=models.CASCADE,
        related_name='messages', verbose_name='room'
    )
    text = models.CharField(max_length=1000)
    
    class Meta:
        db_table = 'Message'
        verbose_name = _('message')
        verbose_name_plural = _('messages')

    # def clean(self, *args, **kwargs):
    #     if self.author not in self.room.members.all():
    #         raise ValidationError(
    #             'Author is not member of the room'
    #         )
    #     super().clean(*args, **kwargs)