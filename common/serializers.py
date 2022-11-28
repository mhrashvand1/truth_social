from rest_framework import serializers
from account.models import User


class CommonUserSerializer(serializers.Serializer):
    
    name = serializers.CharField(read_only=True)
    username = serializers.CharField(read_only=True)
    bio = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()
    followed_you = serializers.SerializerMethodField()
    is_followed = serializers.SerializerMethodField()
    
    def get_bio(self, obj):
        return str(obj.profile.bio)
    
    def get_avatar(self, obj):
        request = self.context['request']
        url = obj.profile.avatar.url
        uri = request.build_absolute_uri(url)
        return uri
   
    def get_is_followed(self, obj):
        current_user = self.context['request'].user
        if not current_user.is_authenticated:
            return None
        if obj.followers.filter(username=current_user.username).exists():
            return True
        return False
    
    def get_followed_you(self, obj):
        current_user = self.context['request'].user
        if not current_user.is_authenticated:
            return None
        if obj.followings.filter(username=current_user.username).exists():
            return True
        return False