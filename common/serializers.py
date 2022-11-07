from rest_framework import serializers
from account.models import User


class CommonUserSerializer(serializers.Serializer):
    
    name = serializers.CharField(read_only=True)
    username = serializers.CharField(read_only=True)
    bio = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()
    follows_you = serializers.SerializerMethodField()
    
    def get_bio(self, obj):
        return str(obj.profile.bio)
    
    def get_avatar(self, obj):
        request = self.context['request']
        url = obj.profile.avatar.url
        uri = request.build_absolute_uri(url)
        return uri
    
    def get_follows_you(self, obj):
        current_user = self.context['request'].user
        if current_user in obj.followings.all():
            return True
        return False