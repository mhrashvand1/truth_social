from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.settings import api_settings
from django.contrib.auth.models import update_last_login
from django.contrib.auth import authenticate, get_user_model
from django.utils.translation import gettext_lazy as _
from rest_framework import exceptions, serializers
from django.core.validators import EmailValidator
from django.core.exceptions import ValidationError
from djoser.serializers import ActivationSerializer


class TokenObtainPairSerializer(serializers.Serializer):
    
    username_or_email = serializers.CharField()
    password = serializers.CharField(
        allow_blank=False, required=True, 
        write_only=True, 
        style={'input_type': 'password', 'placeholder': 'Password'}
    )
    
    @classmethod
    def get_token(cls, user):
        return RefreshToken.for_user(user)

    def validate_username_or_email(self, value):
        try:
            email_validator = EmailValidator(message='Invalid email')
            email_validator(value=value)
            
            try:
                user = get_user_model().objects.get(email=value)
                return user.username
            except:
                raise exceptions.AuthenticationFailed(
                    _('Entered values ​​are invalid'), 401
                )     
        
        except ValidationError:
            return value
        

    def validate(self, attrs):
        
        authenticate_kwargs = {
            "username":attrs['username_or_email'],
            'password': attrs['password'],
        }
        
        try:
            authenticate_kwargs['request'] = self.context['request']
        except KeyError:
            pass

        self.user = authenticate(**authenticate_kwargs)

        if not self.user:
           raise exceptions.AuthenticationFailed(
                _('Entered values ​​are invalid'), 401
            )   
           
        if not self.user.is_active:
           raise exceptions.AuthenticationFailed(
                _('User is not active'), 401
            )        
            
        if not self.user.is_email_verified:
            raise exceptions.AuthenticationFailed(
                _('Email is not verified'), 401
            )

        refresh = self.get_token(self.user)
        data = dict()
        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)

        if api_settings.UPDATE_LAST_LOGIN:
            update_last_login(None, self.user)

        return data
