from curses.ascii import US
from django.db import models
from django.contrib.auth import get_user_model
from common.models import BaseModel
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

User = get_user_model() 

class Follow(BaseModel):
    
    from_user = models.ForeignKey(
        to=User, on_delete=models.CASCADE, 
        related_name='follows_from', db_index=True, 
        verbose_name=_('from user')
    )
    to_user = models.ForeignKey(
        to=User, on_delete=models.CASCADE, 
        related_name='follows_to', db_index=True, 
        verbose_name=_('to user')
    )
    
    class Meta:
        db_table = 'Follow'
        verbose_name = _('follow')
        verbose_name_plural = _('follows')
        unique_together = ('from_user', 'to_user')
        
        
class Block(BaseModel):
    
    from_user = models.ForeignKey(
        to=User, on_delete=models.CASCADE, 
        related_name='blocks_from', db_index=True, 
        verbose_name=_('from user')
    )
    to_user = models.ForeignKey(
        to=User, on_delete=models.CASCADE, 
        related_name='blocks_to', db_index=True, 
        verbose_name=_('to user')
    )
    
    class Meta:
        db_table = 'Block'
        verbose_name = _('block')
        verbose_name_plural = _('blocks')
        unique_together = ('from_user', 'to_user')
           
           
class OnlineStatus(models.Model): 
    
    status_choices = [
        (0, 'online'),
        (1, 'offline')
    ]
      
    user = models.OneToOneField(
        to=User, primary_key=True, db_index=True, 
        on_delete=models.CASCADE, related_name='online_status', 
        verbose_name=_('user')
    ) 
    status = models.IntegerField(choices=status_choices, default=1)
    last_seen = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'OnlineStatus'
        verbose_name = _('online status')
        verbose_name_plural = _('online status')
        