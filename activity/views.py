from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from common.serializers import CommonUserSerializer
from activity.serializers import (
    FollowSerializer,
    UnFollowSerializer,
    BlockSerializer,
    UnBlockSerializer
)
from notification.models import Notification
from common.generics import CustomGenericViewSet
from rest_framework.permissions import AllowAny, IsAuthenticated

User = get_user_model()

class FollowViewSet(CustomGenericViewSet):  
        
    def get_permissions(self):
        if self.action in ['followers', 'followings']:
            self.permission_classes = [AllowAny]
        elif self.action in ['follow', 'unfollow']:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()
         
    @property
    def search_fields(self):
        if self.action in ['followers', 'followings']:
            return ['name', 'username']
        return []
     
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
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data) 
    
    @action(methods=['get'], detail=False)
    def followings(self, request, *args, **kwargs):
        username = kwargs.get('username')
        user = get_object_or_404(User, username=username)
        queryset = self.filter_queryset(user.followings.all())
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)  
    
    @action(methods=['post'], detail=False)
    def follow(self, request, *args, **kwargs):  #Notif
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        message = serializer.perform_follow()
        return Response({"detail":message}, 200)
 
    @action(methods=['post'], detail=False)
    def unfollow(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        message = serializer.perform_unfollow()
        return Response({"detail":message}, 200)  
  
       
    
class BlockViewSet(CustomGenericViewSet):
    
    @action(methods=['post'], detail=False, url_name='block', url_path='block')
    def block(self, request, *args, **kwargs):
        return Response(kwargs)
 
    @action(methods=['post'], detail=False, url_name='unblock', url_path='unblock')
    def unblock(self, request, *args, **kwargs):
        return Response(kwargs)
  
    @action(methods=['get'], detail=False, url_name='blockings', url_path='blockings')
    def blockings(self, request, *args, **kwargs):
        return Response(kwargs)