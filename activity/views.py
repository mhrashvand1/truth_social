from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from common.serializers import CommonUserSerializer
from activity.serializers import (
    FollowSerializer,
    UnFollowSerializer,
    BlockSerializer,
    UnBlockSerializer,
    IsBlockedSerializer, 
    BlockedYouSerializer
)
from notification.models import Notification
from common.generics import CustomGenericViewSet
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.generics import GenericAPIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from activity import signals
from activity.throttles import FollowThrottle

User = get_user_model()

class FollowViewSet(CustomGenericViewSet):  
    
    filter_backends = [SearchFilter]        
    search_fields = ['name', 'username']

    def get_throttles(self):
        if self.action == 'follow':
            self.throttle_classes = [FollowThrottle]
        return super().get_throttles()
    
    def get_permissions(self):
        if self.action in ['followers', 'followings']:
            self.permission_classes = [AllowAny]
        else:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()
    
    def get_serializer_class(self):
        if self.action == 'follow':
            return FollowSerializer
        elif self.action == 'unfollow':
            return UnFollowSerializer
        else:
            return CommonUserSerializer
    
    @action(methods=['get'], detail=False)
    def followers(self, request, *args, **kwargs):
        username = kwargs.get('username')
        user = get_object_or_404(User, username=username)
        queryset = self.filter_queryset(user.followers.all())
        return self.paginated_response(queryset)
    
    @action(methods=['get'], detail=False)
    def followings(self, request, *args, **kwargs):
        username = kwargs.get('username')
        user = get_object_or_404(User, username=username)
        queryset = self.filter_queryset(user.followings.all()) 
        return self.paginated_response(queryset)
    
    # return followers that followed by you
    @action(methods=['get'], detail=False)
    def followed_by(self, request, *args, **kwargs):
        username = kwargs.get('username')
        user = get_object_or_404(User, username=username)
        current_user = request.user
        queryset = self.filter_queryset(
            user.followers.filter(followers=current_user)
        )
        return self.paginated_response(queryset)
        
    @action(methods=['get'], detail=False)
    def followed_you(self, request, *args, **kwargs):
        username = kwargs.get('username')
        user = get_object_or_404(User, username=username)
        current_user = request.user
        result = False
        qs = user.followings.filter(username=current_user.username)
        if qs.exists():
            result = True
        return Response({"followed_you":result})
      
    @action(methods=['get'], detail=False)
    def is_followed(self, request, *args, **kwargs):
        username = kwargs.get('username')
        user = get_object_or_404(User, username=username)
        current_user = request.user
        result = False
        qs = user.followers.filter(username=current_user.username)
        if qs.exists():
            result = True
        return Response({"is_followed":result})
           
    @action(methods=['post'], detail=False)
    def follow(self, request, *args, **kwargs): 
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        message = serializer.perform_follow()
        signals.follow_user.send(
            sender=self.__class__, 
            current_user=request.user,
            target_user=serializer.validated_data['username'],
            request=request
        )
        return Response({"detail":message}, 200)
 
    @action(methods=['post'], detail=False)
    def unfollow(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        message = serializer.perform_unfollow()
        signals.unfollow_user.send(
            sender=self.__class__, 
            current_user=request.user,
            target_user=serializer.validated_data['username'],
            request=request
        )
        return Response({"detail":message}, 200)  
  
       
    
class BlockViewSet(CustomGenericViewSet):
    
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter]
    search_fields = ['name', 'username']
       
    def get_serializer_class(self):
        if self.action == 'block':
            return BlockSerializer
        elif self.action == 'unblock':
            return UnBlockSerializer
        elif self.action == 'is_blocked':
            return IsBlockedSerializer
        elif self.action == 'blocked_you':
            return BlockedYouSerializer
        else:
            return CommonUserSerializer
            
    @action(methods=['post'], detail=False, url_name='block', url_path='block')
    def block(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        message = serializer.perform_block()
        signals.block_user.send(
            sender=self.__class__,
            current_user=request.user,
            target_user=serializer.validated_data['username'],
            request=request
        )
        return Response({"detail":message}, 200)
 
    @action(methods=['post'], detail=False, url_name='unblock', url_path='unblock')
    def unblock(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        message = serializer.perform_unblock()
        return Response({"detail":message}, 200)

    @action(methods=['get'], detail=False, url_name='blockings', url_path='blockings')
    def blockings(self, request, *args, **kwargs):
        user = request.user
        queryset = self.filter_queryset(user.blockings.all())
        return self.paginated_response(queryset)
    
    
    @action(methods=['post'], detail=False, url_path='is_blocked', url_name='is_blocked')
    def is_blocked(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = serializer.is_blocked()
        return Response(result, 200)
    
    @action(methods=['post'], detail=False, url_path='blocked_you', url_name='blocked_you')
    def blocked_you(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = serializer.blocked_you()
        return Response(result, 200)