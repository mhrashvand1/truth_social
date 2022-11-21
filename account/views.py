from rest_framework_simplejwt.views import TokenViewBase
from account.serializers import TokenObtainPairSerializer, TokenBlackListSerializer
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils.translation import gettext_lazy as _
from djoser.views import UserViewSet as BaseUserViewSet
from rest_framework.decorators import action
from pathlib import Path
from django.core.files import File
from config.settings import MEDIA_ROOT
from djoser.conf import settings as djoser_settings
from rest_framework import status
from django.contrib.auth import get_user_model
from djoser.compat import get_user_email
from django.db.models import Q 
from account.permissions import UserRetrievePermissions, UserUpdatePermissions
from common.paginations import StandardPagination

User = get_user_model()


class TokenObtainPairView(TokenViewBase):
    serializer_class = TokenObtainPairSerializer


class TokenBlackListView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TokenBlackListSerializer
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        refresh = serializer.validated_data['refresh']
        try:
            token = RefreshToken(refresh)
            token.blacklist()
            return Response({"detail":"refresh token added to blacklist"}, 200)
        except:
            return Response({"detail":"token is invalid"}, 400)
        
   
        
class UserViewSet(BaseUserViewSet):
    
    pagination_class = StandardPagination
    lookup_field = 'username'
    
    def perform_update(self, serializer):
        serializer.save()
        
    def get_permissions(self):
        if self.action == 'update':
            self.permission_classes = [UserUpdatePermissions]
        elif self.action == 'retrieve':
            self.permission_classes = [UserRetrievePermissions]
        return super().get_permissions()
        
    @action(methods=['get'], detail=False, url_path='delete_avatar', url_name='delete_avatar')
    def delete_avatar(self, request, *args, **kwargs):
        user = self.get_instance()
        profile = user.profile
        profile.avatar.delete()
        
        no_avatar_path = MEDIA_ROOT.as_posix() + '/no_avatar.png'
        path = Path(no_avatar_path)
        
        with path.open(mode='rb') as f:
            profile.avatar = File(f, name=path.name)
            profile.save()

        return Response({"detail":"avatar deleted."}, 200)
    
    
    @action(["post"], detail=False)
    def resend_activation(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        query = Q(is_active=False) | Q(is_email_verified=False)
        user = serializer.get_user(query=query)

        if not djoser_settings.SEND_ACTIVATION_EMAIL or not user:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        context = {"user": user}
        to = [get_user_email(user)]
        djoser_settings.EMAIL.activation(self.request, context).send(to)

        return Response(status=status.HTTP_204_NO_CONTENT)
    
    
    @action(["post"], detail=False)
    def reset_password(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        query = Q(is_active=True) & Q(is_email_verified=True)
        user = serializer.get_user(query)

        if user:
            context = {"user": user}
            to = [get_user_email(user)]
            djoser_settings.EMAIL.password_reset(self.request, context).send(to)

        return Response(status=status.HTTP_204_NO_CONTENT)
    
    
    @action(["post"], detail=False, url_path="reset_{}".format(User.USERNAME_FIELD))
    def reset_username(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        query = Q(is_active=True) & Q(is_email_verified=True)
        user = serializer.get_user(query)
        
        if user:
            context = {"user": user}
            to = [get_user_email(user)]
            djoser_settings.EMAIL.username_reset(self.request, context).send(to)

        return Response(status=status.HTTP_204_NO_CONTENT)