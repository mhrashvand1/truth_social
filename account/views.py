from rest_framework_simplejwt.views import TokenViewBase
from account.serializers import TokenObtainPairSerializer


class TokenObtainPairView(TokenViewBase):
    serializer_class = TokenObtainPairSerializer


