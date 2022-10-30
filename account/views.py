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
    
    def perform_update(self, serializer):
        serializer.save()
        
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