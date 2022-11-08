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
from common.mixins import PaginationMixin, FilterMixin
from common.paginations import StandardPagination
from notification.models import Notification
from common.generics import CustomGenericViewSet
from notification.serializers import(
    BellEnableSerializer,
    BellDisableSerializer,
    ChangeBellPrioritySerializer,
    BellStatusSerializer,
    NotificationSerializer
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter

class BellViewSet(CustomGenericViewSet):
    
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter]        
    search_fields = ['name', 'username']
    
    def get_serializer_class(self):
        if self.action == 'enable_bell':
            return BellEnableSerializer
        elif self.action == 'disable_bell':
            return BellDisableSerializer
        elif self.action == 'change_priority':
            return ChangeBellPrioritySerializer
        elif self.action == 'bell_status':
            return BellStatusSerializer
        else:
            return CommonUserSerializer
    
    @action(methods=['post'], detail=False, url_path='enable_bell', url_name='enable_bell')
    def enable_bell(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_raise_exception=True)
        message = serializer.perform_bell_enable()
        return Response(message, 200)
    
    @action(methods=['post'], detail=False, url_path='disable_bell', url_name='disable_bell')
    def disable_bell(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_raise_exception=True)
        message = serializer.perform_bell_disable()
        return Response(message, 200)

    @action(methods=['put'], detail=False, url_path='change_priority', url_name='change_priority')
    def change_priority(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        message = serializer.perform_change()
        return Response(message, 200)
    
    @action(methods=['post'], detail=False, url_path='bell_status', url_name='bell_status')
    def bell_status(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = serializer.get_bell_status()
        return Response(result, 200) 
    
    @action(methods=['get'], detail=False, url_path='bell_enablings', url_name='bell_enablings')
    def bell_enablings(self, request, *args, **kwargs):
        user = request.user
        queryset = self.filter_queryset(user.bell_enablings.all())
        return self.paginated_response(queryset)


class NotificationViewSet(
    ListModelMixin,
    RetrieveModelMixin,
    GenericViewSet
):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        return NotificationSerializer
    
    def get_queryset(self):
        return Notification.objects.filter(to=self.request.user)
    