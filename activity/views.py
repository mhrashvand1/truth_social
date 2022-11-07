from rest_framework.viewsets import ModelViewSet, ViewSet, GenericViewSet
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import (
    ListModelMixin,
    CreateModelMixin,
    RetrieveModelMixin, 
    DestroyModelMixin,
    UpdateModelMixin
)
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from common.serializers import CommonUserSerializer
from common.mixins import PaginationMixin
from common.paginations import StandardPagination
from activity.serializers import (
    FollowSerializer,
    UnFollowSerializer,
    BlockSerializer,
    UnBlockSerializer
)
from notification.models import Notification


User = get_user_model()


class FollowViewSet(PaginationMixin, ViewSet):  
    
    pagination_class = StandardPagination
    
    def get_serializer_class(self):
        if self.action == 'follow':
            return FollowSerializer
        elif self.action == 'unfollow':
            return UnFollowSerializer
        else:
            return CommonUserSerializer
    
    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs.setdefault('context', self.get_serializer_context())
        return serializer_class(*args, **kwargs)
    
    def get_serializer_context(self):
        return {
            'request': self.request,
            'format': self.format_kwarg,
            'view': self
        }
    
    @action(methods=['get'], detail=False)
    def followers(self, request, *args, **kwargs):
        username = kwargs.get('username')
        user = get_object_or_404(User, username=username)
        queryset = user.followers.all()
        
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
        queryset = user.followings.all()
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)  
    
    @action(methods=['post'], detail=False)
    def follow(self, request, *args, **kwargs):
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
  
       
    
class BlockViewSet(ViewSet):
    
    @action(methods=['post'], detail=False, url_name='block', url_path='block')
    def block(self, request, *args, **kwargs):
        return Response(kwargs)
 
    @action(methods=['post'], detail=False, url_name='unblock', url_path='unblock')
    def unblock(self, request, *args, **kwargs):
        return Response(kwargs)
  
    @action(methods=['get'], detail=False, url_name='blockings', url_path='blockings')
    def blockings(self, request, *args, **kwargs):
        return Response(kwargs)