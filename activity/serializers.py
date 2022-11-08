from rest_framework import serializers
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError, NotFound
from activity.models import Follow, Block

User = get_user_model()


class FollowSerializer(serializers.Serializer):
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
            raise ValidationError('Can not follow/unfollow yourself.')
        
        if current_user.followings.filter(username=target_user.username).exists():
            raise ValidationError(f'User with username {value} has already followed.')
             
        return target_user
      
    def perform_follow(self):
        current_user = self.context['request'].user
        target_user = self.validated_data['username']
        Follow.objects.create(
            from_user=current_user, to_user=target_user
        )
        return f"{current_user.username} follows {target_user.username} successfully."


class UnFollowSerializer(serializers.Serializer):
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
            raise ValidationError('Can not follow/unfollow yourself.')
        
        if target_user not in current_user.followings.all(): ##
            raise ValidationError(f'User with username {value} is not followed.')
            
        return target_user
      
    def perform_unfollow(self):
        current_user = self.context['request'].user
        target_user = self.validated_data['username']
        try:
            Follow.objects.get(
                from_user=current_user, to_user=target_user
            ).delete()
        except:
            pass
        return f"{current_user.username} unfollows {target_user.username} successfully."



class BlockSerializer(serializers.Serializer):
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
            raise ValidationError('Can not block/unblock yourself.')
        
        if target_user in current_user.blockings.all(): ##
            raise ValidationError(f'User with username {value} has already blocked.')
            
        return target_user
      
    def perform_block(self):
        current_user = self.context['request'].user
        target_user = self.validated_data['username']
        Block.objects.create(
            from_user=current_user, to_user=target_user
        )
        return f"{current_user.username} blocks {target_user.username} successfully."


class UnBlockSerializer(serializers.Serializer):
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
            raise ValidationError('Can not block/unblock yourself.')
        
        if target_user not in current_user.blockings.all(): ##
            raise ValidationError(f'User with username {value} is not blocked.')
            
        return target_user
      
    def perform_unblock(self):
        current_user = self.context['request'].user
        target_user = self.validated_data['username']
        try:
            Block.objects.get(
                from_user=current_user, to_user=target_user
            ).delete()
        except:
            pass
        return f"{current_user.username} unblocks {target_user.username} successfully."


class IsBlockedSerializer(serializers.Serializer):
    username = serializers.CharField(
        max_length=150, validators=[UnicodeUsernameValidator], allow_blank=False, required=True
    )
    
    def validate_username(self, value):
        qs = User.objects.filter(username=value)
        if not qs.exists():
            raise NotFound()
        return qs.first()
    
    def is_bloked(self):
        current_user = self.context['request'].user
        target_user = self.validated_data['username']
        result = dict()
        if current_user.blockings.filter(username=target_user.username).exists():
            result['is_blocked'] = True
        else:
            result['is_blocked'] = False
            
        return result