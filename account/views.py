from rest_framework_simplejwt.views import TokenViewBase
from account.serializers import TokenObtainPairSerializer, TokenBlackListSerializer
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils.translation import gettext_lazy as _
from djoser.views import UserViewSet as BaseUserViewSet


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