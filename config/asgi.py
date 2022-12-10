import os
import django
from channels.http import AsgiHandler
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.sessions import SessionMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator
from chat import routers as chat_router


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

application = ProtocolTypeRouter(
    {
        "http": AsgiHandler(),
        "websocket":AllowedHostsOriginValidator(
            SessionMiddlewareStack(
                AuthMiddlewareStack(
                    URLRouter(
                        chat_router.websocket_urlpatterns
                    )
                )
            )
        )
    }
)