from email.policy import default
from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser
from django.core.mail import send_mail
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import PermissionsMixin, UserManager
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.validators import MinLengthValidator
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.exceptions import ValidationError
from common.models import BaseModel
from account.utils import get_avatar_path


class User(AbstractBaseUser, PermissionsMixin, BaseModel):

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
        db_table = 'User'

    username_validator = UnicodeUsernameValidator()
    username = models.CharField(
        _("username"),
        max_length=150,
        unique=True,
        help_text=_(
            "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
        ),
        validators=[username_validator],
        error_messages={
            "unique": _("A user with that username already exists."),
        },
        db_index=True,
    )  
    email = models.EmailField(_("email address"),  unique=True) 
    
    is_email_verified = models.BooleanField(
        _("is_email_verified"),
        default=False,
    )
    find_me_by_email = models.BooleanField(
        _("find_me_by_email"), 
        default=True
    )
    
    name = models.CharField(_("name"), max_length=150)
    
    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into this admin site."),
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)

    objects = UserManager()

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    def __str__(self) -> str:
        return str(self.username)
    
    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def get_full_name(self):
        full_name = "%s" % (self.name)
        return full_name.strip()

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)



class Profile(models.Model):
    
    user = models.OneToOneField(
        to='User', primary_key=True, db_index=True, 
        on_delete=models.CASCADE, related_name='profile', 
        verbose_name=_('user')
    )
    avatar = models.ImageField(
        verbose_name=_('avatar'), default='no_avatart.png',
        blank=True, upload_to=get_avatar_path
    )
    bio = models.CharField(verbose_name=_('bio'), max_length=150, blank=True)
    date_of_birth = models.DateTimeField(verbose_name=_('date of birth'), null=True)
    website = models.URLField(verbose_name=_('website'), blank=True)
