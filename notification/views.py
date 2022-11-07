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


class BellViewSet(CustomGenericViewSet): 
    pass

class NotificationViewSet(CustomGenericViewSet):
    pass