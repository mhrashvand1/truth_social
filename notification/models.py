from django.db import models
from django.contrib.auth import get_user_model
from common.models import BaseModel
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from notification.constants import (
    PRIORITIES, 
    NOTIF_TYPES, 
)


User = get_user_model() 


class Bell(BaseModel):
    
    from_user = models.ForeignKey(
        to=User, on_delete=models.CASCADE, 
        related_name='bells_from', db_index=True, 
        verbose_name=_('from user')
    )
    to_user = models.ForeignKey(
        to=User, on_delete=models.CASCADE, 
        related_name='bells_to', db_index=True, 
        verbose_name=_('to user')
    )   
    priority = models.IntegerField(
        verbose_name=_('priority'),
        choices=PRIORITIES
    )
    
    class Meta:
        db_table = 'Bell'
        verbose_name = _('bells')
        verbose_name_plural = _('bells')
        unique_together = ('from_user', 'to_user')
           
           
class Notification(BaseModel):
    
    to = models.ForeignKey(
        to=User, 
        related_name='notifications', 
        on_delete=models.CASCADE,
        db_index=True,
        verbose_name=_('to user')
    )
    notif_type = models.IntegerField(
        verbose_name=_('notification type'), 
        choices=NOTIF_TYPES
    )
    message = models.CharField(
        max_length=300, 
        verbose_name=_('message')
    )
    priority = models.IntegerField(
        verbose_name=_('priority'),
        choices=PRIORITIES, 
    )
    
    has_read = models.BooleanField(
        verbose_name=_('has read'),
        default=False
    )

    class Meta:
        db_table = 'Notification'
        verbose_name = _('notification')
        verbose_name_plural = _('notifications')
        