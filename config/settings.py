from pathlib import Path
from decouple import config
from datetime import timedelta

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config("SECRET_KEY", default="xxx")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config("DEBUG", default=False)

ALLOWED_HOSTS = ['127.0.0.1']

INTERNAL_IPS = [
    "127.0.0.1",
]

# Application definition

DEFAULT_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',   
]

THIRD_PARTY_PACKAGES = [
    'channels',
    "django_filters",
    "rest_framework",
    "djoser",
    'rest_framework_simplejwt.token_blacklist',
    'django_cleanup.apps.CleanupConfig',
    "drf_yasg",
    # "debug_toolbar",
]

PROJECT_APPS = [
    'account.apps.AccountConfig',
    'activity.apps.ActivityConfig',
    'chat.apps.ChatConfig',
    'core.apps.CoreConfig',
    'timeline.apps.TimelineConfig',
    'search.apps.SearchConfig',
    'notification.apps.NotificationConfig',
]

INSTALLED_APPS = DEFAULT_APPS + THIRD_PARTY_PACKAGES + PROJECT_APPS


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # "debug_toolbar.middleware.DebugToolbarMiddleware",
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# user mdoel
AUTH_USER_MODEL = 'account.User'

# email backend 
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": config("DB_ENGINE", default="django.db.backends.sqlite3"),
        "NAME": config("DB_NAME", default="db.sqlite3"),
        "USER": config("DB_USER", default="foo"),
        "PASSWORD": config("DB_PASSWORD", default="foo"),
        "HOST": config("DB_HOST", default="localhost"),
        "PORT": config("DB_PORT", default=5432),
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Tehran'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'static'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# channels
ASGI_APPLICATION = 'config.asgi.application'

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("127.0.0.1", 6379)],
        },
    },
}
LOGIN_REDIRECT_URL = 'http://127.0.0.1:8000/chat'
LOGOUT_REDIRECT_URL = 'http://127.0.0.1:8000/chat/login/'


# drf
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES':(
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_FILTER_BACKENDS':(
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter'
    ),
    'DEFAULT_PAGINATION_CLASS':'common.paginations.StandardPagination'
}

# simpleJWT
SIMPLE_JWT = {
    "AUTH_HEADER_TYPES": ("JWT", "Bearer", "jwt", "bearer"),
    "ACCESS_TOKEN_LIFETIME": timedelta(days=360), # seconds=60
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1000), # days=100
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
}

# djoser 
DJOSER = {
    "ACTIVATION_URL": "activate/{uid}/{token}/",
    "PASSWORD_RESET_CONFIRM_URL": "reset_password/{uid}/{token}/",  # dimain?
    "USERNAME_RESET_CONFIRM_URL": "reset_username/{uid}/{token}/",
    "SEND_ACTIVATION_EMAIL": True,
    #"SEND_CONFIRMATION_EMAIL":True, 
    "LOGOUT_ON_PASSWORD_CHANGE": True,
    "PASSWORD_RESET_SHOW_EMAIL_NOT_FOUND": True,
    "SERIALIZERS": {
        "user_create": "account.serializers.UserCreateSerializer",
        "user": "account.serializers.UserSerializer",
        "current_user":"account.serializers.CurrentUserSerializer",
        'password_reset': 'account.serializers.SendEmailResetSerializer',
        'username_reset': 'account.serializers.SendEmailResetSerializer',
        'activation': 'account.serializers.ActivationSerializer',
        'set_username': 'account.serializers.SetUsernameSerializer',
        'username_reset_confirm': 'account.serializers.UsernameResetConfirmSerializer',
    },
    "EMAIL": {
        'activation': 'account.email.ActivationEmail',
        'confirmation': 'account.email.ConfirmationEmail',
        'password_reset': 'account.email.PasswordResetEmail',
        'password_changed_confirmation': 'account.email.PasswordChangedConfirmationEmail',
        'username_changed_confirmation': 'account.email.UsernameChangedConfirmationEmail',
        'username_reset': 'account.email.UsernameResetEmail',
    },
    "TOKEN_MODEL":None,
    "HIDE_USERS":False
}
FRONTEND_DOMAIN = "127.0.0.1:8000"


# SESSION 
SESSION_ENGINE = "django.contrib.sessions.backends.db"
