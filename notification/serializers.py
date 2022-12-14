from rest_framework import serializers
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError, NotFound
from notification.models import Bell, Notification
from notification.constants import PRIORITIES, NOTIF_TYPES
from activity.models import Block
from common.utils import querystring_to_dict
from django.urls import reverse

User = get_user_model()

class BellEnableSerializer(serializers.Serializer):
    username = serializers.CharField(
        max_length=150, validators=[UnicodeUsernameValidator], allow_blank=False, required=True
    )
    priority = serializers.ChoiceField(choices=PRIORITIES, default=3)

    def validate_username(self, value):

        qs = User.objects.filter(username=value)
        if not qs.exists():
            raise ValidationError(f'There is not user with username {value} .')
        
        target_user = qs.first()
        current_user = self.context['request'].user
        
        if current_user == target_user:
            raise ValidationError(
                f"You can not enable/disable the bell of yourself."
            )
            
        if current_user.bell_enablings.filter(username=target_user.username).exists():
            raise ValidationError(
                f'The bell of user with username {value} has already enabled.'
            )
        
        if not current_user.followings.filter(username=target_user.username).exists():
            raise ValidationError(
                f'You can not enable the bell of user with username {value} , because you have not followed it.'
            )
            
        if current_user.blockings.filter(username=target_user.username).exists():
            raise ValidationError(
                f'You can not enable the bell of user with username {value} , bacause you have blocked it.'
            )
            
        if current_user.blockers.filter(username=target_user.username).exists():
            raise ValidationError(
                f'You can not enable the bell of user with username {value} , because you are blocked.'
            )
            
        return target_user
    
    def perform_bell_enable(self):
        data = self.validated_data
        target_user = data['username']
        priority = data['priority']
        current_user = self.context['request'].user
        Bell.objects.create(
            from_user=current_user, 
            to_user=target_user,
            priority=priority
        )
        return f"{current_user.username} enables the bell of {target_user.username} successfully."
    


class BellDisableSerializer(serializers.Serializer):
    username = serializers.CharField(
        max_length=150, validators=[UnicodeUsernameValidator], allow_blank=False, required=True
    )

    def validate_username(self, value):

        qs = User.objects.filter(username=value)
        if not qs.exists():
            raise ValidationError(f'There is not user with username {value} .')
        
        target_user = qs.first()
        current_user = self.context['request'].user
        
        if current_user == target_user:
            raise ValidationError(
                f"You can not enable/disable the bell of yourself."
            )
            
        if not current_user.bell_enablings.filter(username=target_user.username).exists():
            raise ValidationError(
                f'The bell of user with username {value} is not enable.'
            )
            
        return target_user
    
    def perform_bell_disable(self):
        current_user = self.context['request'].user
        target_user = self.validated_data['username']
        Bell.objects.filter(
            from_user=current_user, to_user=target_user
        ).delete()
        return f"{current_user.username} disables the bell of {target_user.username} successfully."


class ChangeBellPrioritySerializer(serializers.Serializer):
    
    username = serializers.CharField(
        max_length=150, validators=[UnicodeUsernameValidator], allow_blank=False, required=True
    )
    priority = serializers.ChoiceField(choices=PRIORITIES, default=3)


    def validate_username(self, value):
        
        current_user = self.context['request'].user
        qs = current_user.bell_enablings.filter(username=value)
        if not qs.exists():
            raise ValidationError(
                f'User with username {value} is not in your bell enablings.'
            )
        
        target_user = qs.first()
        return target_user
    
    def perform_change(self):
        current_user = self.context['request'].user
        target_user = self.validated_data['username']
        priority = self.validated_data['priority']
        try:
            bell = Bell.objects.get(from_user=current_user, to_user=target_user)
            bell.priority = priority
            bell.save()
        except:
            pass
        
        return f"Bell priority of the user with username {target_user.username} set to {priority}"
    

class BellStatusSerializer(serializers.Serializer):
    username = serializers.CharField(
        max_length=150, validators=[UnicodeUsernameValidator], allow_blank=False, required=True
    )
    
    def validate_username(self, value):
        qs = User.objects.filter(username=value)
        if not qs.exists():
            raise NotFound()
        return qs.first()
    
    def get_bell_status(self):
        current_user = self.context['request'].user
        target_user = self.validated_data['username']
        result = dict()
        qs = Bell.objects.filter(from_user=current_user, to_user=target_user)
        if qs.exists():
            result['status'] = 'enable'
            result['priority'] = qs.first().priority
        else:
            result['status'] = 'disable'
            result['priority'] = None
        return result
    
    
class NotificationSerializer(serializers.ModelSerializer):
    to = serializers.CharField(source='to.username')
    notif_type = serializers.SerializerMethodField()
    message = serializers.SerializerMethodField()
    
    class Meta:
        model = Notification
        fields = ['id', 'to', 'notif_type', 'message', 'priority', 'has_read']
        
        
    def get_notif_type(self, obj):
        return dict(NOTIF_TYPES)[obj.notif_type]
    
    def get_message(self, obj):
        message = querystring_to_dict(obj.message)  
        message_type = message['type'][0]
        handler = getattr(self, f'{message_type}_message_handler')
        return handler(message)
    
    def follow_message_handler(self, message):
        result = dict()
        result['type'] = message['type'][0]
        actor_username = message['actor'][0]
        result['actor'] = self.get_actor_info(username=actor_username) 
        return result
    
    def like_message_handler(self, message):
        result = dict()
        result['type'] = message['type'][0]
        actor_username = message['actor'][0]
        result['actor'] = self.get_actor_info(username=actor_username)
        ... 
        return result
    
    def mention_message_handler(self, message):
        result = dict()
        result['type'] = message['type'][0]
        actor_username = message['actor'][0]
        result['actor'] = self.get_actor_info(username=actor_username)
        ... 
        return result
        
    def retweet_message_handler(self, message):
        result = dict()
        result['type'] = message['type'][0]
        actor_username = message['actor'][0]
        result['actor'] = self.get_actor_info(username=actor_username)
        ... 
        return result
    
    def new_tweet_message_handler(self, message):
        result = dict()
        result['type'] = message['type'][0]
        actor_username = message['actor'][0]
        result['actor'] = self.get_actor_info(username=actor_username)
        ... 
        return result
    
    def truth_social_message_handler(self, message):
        pass
    
    def get_actor_info(self, username):
        build_absolute_uri = self.context['request'].build_absolute_uri
        result = dict()
        try:
            actor = User.objects.get(username=username)
            result['name'] = actor.name
            result['avatar'] = build_absolute_uri(actor.profile.avatar.url)
            result['url'] = build_absolute_uri(
                reverse('account:user-detail', kwargs={"username":username})
            )
        except User.DoesNotExist:
            result = None
        
        return result
    
    def get_tweet_info(self, id):
        pass