from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.settings import api_settings
from django.contrib.auth.models import update_last_login
from django.contrib.auth import authenticate, get_user_model
from django.utils.translation import gettext_lazy as _
from rest_framework import exceptions, serializers
from django.core.validators import EmailValidator
from django.core.exceptions import ValidationError
from djoser.serializers import (
    UserSerializer as BaseUserSerializer, 
    UserCreateSerializer as BaseUserCreateSerializer, 
    ActivationSerializer as BaseActivationSerializer,
    UidAndTokenSerializer,
    SetUsernameSerializer as BaseSetUsernameSerializer,
    SetUsernameRetypeSerializer,
    UsernameResetConfirmSerializer as BaseUsernameResetConfirmSerializer,
    UsernameResetConfirmRetypeSerializer,
    CurrentPasswordSerializer,
    UidAndTokenSerializer
)
from django.db import IntegrityError, transaction
from djoser.conf import settings
from djoser.compat import get_user_email, get_user_email_field_name
from django.db.models import Q 
from account.models import Profile
from account.constants import RESERVED_WORDS
from random import sample
from django.urls import reverse
from notification.models import Bell
from django.contrib.auth.validators import UnicodeUsernameValidator
from account.validators import UsernameUniqueValidator
from rest_framework.validators import UniqueValidator

User = get_user_model()

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
            email_validator(value=value) # raise error if value was not email
            qs = get_user_model().objects.filter(email=value) 
        except ValidationError:
            qs = get_user_model().objects.filter(username=value)
        
        if not qs.exists():
            raise exceptions.AuthenticationFailed(
                _('Entered values ​​are invalid(1)'), 401
            )   
            
        user = qs.first()
        if not user.is_active:    
            raise exceptions.AuthenticationFailed(
                _('User is not active'), 401
            ) 
            
        if not user.is_email_verified: 
            raise exceptions.AuthenticationFailed(
                _('Email is not verified'), 401
            )
                 
        return str(user.username)   


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
                _('Entered values ​​are invalid(2)'), 401
            )   

        refresh = self.get_token(self.user)
        data = dict()
        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)

        if api_settings.UPDATE_LAST_LOGIN:
            update_last_login(None, self.user)

        return data


class TokenBlackListSerializer(serializers.Serializer):
    refresh = serializers.CharField(required=True, allow_blank=False)
    
    
class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ["avatar", "bio", "date_of_birth", "website"]
  
    
class UserSerializer(serializers.ModelSerializer):  
    profile = ProfileSerializer(read_only=True)
    is_followed = serializers.SerializerMethodField()
    followed_you = serializers.SerializerMethodField()
    followed_by = serializers.SerializerMethodField()
    is_blocked = serializers.SerializerMethodField()
    blocked_you = serializers.SerializerMethodField()
    bell_status = serializers.SerializerMethodField()
    
    class Meta:
        model = get_user_model()
        fields = [
            "id", "username", "name", "profile", 
            "is_followed", "followed_you", "followed_by", "is_blocked",
            "blocked_you", "bell_status"
        ]
        read_only_fields = [
            "id", "username", "name", "profile", 
            "is_followed", "followed_you", "followed_by", "is_blocked",
            "blocked_you", "bell_status"
        ]

    def get_is_followed(self, obj):
        current_user = self.context['request'].user
        if not current_user.is_authenticated:
            return None
        if obj.followers.filter(username=current_user.username).exists():
            return True
        return False

    def get_followed_you(self, obj):
        current_user = self.context['request'].user
        if not current_user.is_authenticated:
            return None
        if obj.followings.filter(username=current_user.username).exists():
            return True
        return False

    def get_followed_by(self, obj):
        request = self.context['request']
        current_user = request.user
        if not current_user.is_authenticated:
            return None
        qs = obj.followers.filter(followers=current_user)
        count = qs.count()
        samples = qs if count<3 else sample(set(qs), k=2)
        result = dict()
        result['count'] = count
        result['samples'] = dict()
        n = 1
        for sample in samples:
            result['samples'][f'{n}'] = {
                "username":sample.username, 
                "name":sample.name, 
                "avatar":request.build_absolute_uri(sample.profile.avatar.url)
            }
            n += 1
        result['others_you_know_count'] = count - len(samples)
        result['followed_by_url'] = request.build_absolute_uri(
            reverse(
                'activity:user-followed_by', kwargs={"username":obj.username}
            )
        )
        return result
    
    def get_is_blocked(self, obj):
        current_user = self.context['request'].user
        if not current_user.is_authenticated:
            return None
        if current_user.blockings.filter(username=obj.username).exists():
            return True
        return False 
        
    def get_blocked_you(self, obj):
        current_user = self.context['request'].user
        if not current_user.is_authenticated:
            return None
        if current_user.blockers.filter(username=obj.username).exists():
            return True
        return False 

    def get_bell_status(self, obj):
        current_user = self.context['request'].user
        if not current_user.is_authenticated:
            return None
        result = dict()
        qs = Bell.objects.filter(from_user=current_user, to_user=obj)
        if qs.exists():
            result['status'] = 'enable'
            result['priority'] = qs.first().priority
        else:
            result['status'] = 'disable'
            result['priority'] = None
        return result


class CurrentUserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(required=False)

    class Meta:
        model = get_user_model()
        fields = [
            "id", "username", "email", "name", "profile",
            "is_email_verified", "is_active", "find_me_by_email", 
        ]
        read_only_fields = [
            "id", "email", "is_email_verified", 
            "is_active", "username"
        ]
        
    def update(self, instance, validated_data):
        try:
            profile_data = validated_data.pop('profile')
        except:
            profile_data = None
        
        if profile_data:
            profile = instance.profile
            profile.avatar = profile_data.get('avatar', profile.avatar)
            profile.bio = profile_data.get('bio', profile.bio)
            profile.date_of_birth = profile_data.get('date_of_birth', profile.date_of_birth)
            profile.website = profile_data.get('website', profile.website)
            profile.save()
        
        instance.name = validated_data.get('name', instance.name)
        instance.find_me_by_email = validated_data.get('find_me_by_email', instance.find_me_by_email)
        instance.save()
        return instance
    

class UserCreateSerializer(BaseUserCreateSerializer):

    re_password = serializers.CharField(
        allow_blank=False, required=True, 
        write_only=True, 
        style={'input_type': 'password', 'placeholder': 'Password'}
    )
    username = serializers.CharField(
        help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.',
        max_length=150, 
        validators=[
            UnicodeUsernameValidator(), 
            UsernameUniqueValidator(queryset=User.objects.all())
        ],
        required=True,
        allow_blank=False
    )
    
    class Meta:
        model = get_user_model()
        fields = ["id", "username", "email", "password", "re_password", "name"]
     
    def validate_username(self, value):
        if value in RESERVED_WORDS or value.lower() in RESERVED_WORDS:
            raise serializers.ValidationError(
                f"{value} is a reserved word."
            )
        return value
     
    def validate(self, attrs):
        self.fields.pop("re_password", None)
        re_password = attrs.pop("re_password")
        attrs = super().validate(attrs)
        if attrs["password"] == re_password:
            return attrs
        else:
            self.fail("password_mismatch")
                
    def perform_create(self, validated_data):
        with transaction.atomic():
            user = get_user_model().objects.create_user(**validated_data)
            if settings.SEND_ACTIVATION_EMAIL:
                user.is_active = False
                user.is_email_verified = False
                user.save(update_fields=["is_active", "is_email_verified"])
        return user


class UserFunctionsMixin:
    def get_user(self, query):
        try:
            user = User._default_manager.get(
                query,
                **{self.email_field: self.data.get(self.email_field, "")},
            )
            if user.has_usable_password():
                return user
        except User.DoesNotExist:
            pass
        if (
            settings.PASSWORD_RESET_SHOW_EMAIL_NOT_FOUND
            or settings.USERNAME_RESET_SHOW_EMAIL_NOT_FOUND
        ):
            self.fail("email_not_found")


class SendEmailResetSerializer(serializers.Serializer, UserFunctionsMixin):
    default_error_messages = {
        "email_not_found": settings.CONSTANTS.messages.EMAIL_NOT_FOUND
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.email_field = get_user_email_field_name(User)
        self.fields[self.email_field] = serializers.EmailField()


class ActivationSerializer(UidAndTokenSerializer):
    
    default_error_messages = {
        "stale_token": settings.CONSTANTS.messages.STALE_TOKEN_ERROR
    }
    
    def validate(self, attrs):
        attrs = super().validate(attrs)
        if not self.user.is_active or not self.user.is_email_verified: 
            return attrs
        raise exceptions.PermissionDenied(self.error_messages["stale_token"])
 


class SetUsernameSerializer(serializers.ModelSerializer):
    
    new_username = serializers.CharField(
        help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.',
        max_length=150, 
        validators=[
            UnicodeUsernameValidator(), 
            UsernameUniqueValidator(queryset=User.objects.all())
        ],
        required=True,
        allow_blank=False
    )
    current_password = serializers.CharField(
        style={"input_type": "password"},
        required=True,
        allow_blank=False
    )
     
    default_error_messages = {
        "invalid_password": settings.CONSTANTS.messages.INVALID_PASSWORD_ERROR
    }
     
    class Meta:
        model = User
        fields = ('new_username', "current_password")

    def validate_new_username(self, value):
        if value in RESERVED_WORDS or value.lower() in RESERVED_WORDS:
            raise serializers.ValidationError(
                f"{value} is a reserved word."
            )
        return value
    
    def validate_current_password(self, value):
        is_password_valid = self.context["request"].user.check_password(value)
        if is_password_valid:
            return value
        else:
            self.fail("invalid_password")  
    
    def save(self, **kwargs):
        self.validated_data = {'username':self.validated_data['new_username']}
        return super().save(**kwargs)
    
    
    
class UsernameResetConfirmSerializer(UidAndTokenSerializer , serializers.ModelSerializer):

    new_username = serializers.CharField(
        help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.',
        max_length=150, 
        validators=[
            UnicodeUsernameValidator(), 
            UsernameUniqueValidator(queryset=User.objects.all())
        ],
        required=True,
        allow_blank=False
    )
    
    class Meta:
        model = User
        fields = ('new_username', "uid", "token")

    def validate_new_username(self, value):
        if value in RESERVED_WORDS or value.lower() in RESERVED_WORDS:
            raise serializers.ValidationError(
                f"{value} is a reserved word."
            )
        return value
    
    def save(self, **kwargs):
        self.validated_data = {'username':self.validated_data['new_username']}
        return super().save(**kwargs)
    