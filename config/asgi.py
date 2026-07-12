import os
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
http_application = get_asgi_application()

from channels.routing import ProtocolTypeRouter, URLRouter
from notifications.routing import websocket_urlpatterns
from channels.auth import AuthMiddlewareStack

application = ProtocolTypeRouter({
    "http": http_application,
    "websocket": AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})
