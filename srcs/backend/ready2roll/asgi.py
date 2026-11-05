import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ready2roll.settings')
django_asgi_app = get_asgi_application()

from social.middleware import JWTAuthMiddleware
from social.consumers import DMConsumer, SocialConsumer

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": JWTAuthMiddleware(
        URLRouter([
            path("ws/chat/<int:user_id>/", DMConsumer.as_asgi()),
            path("ws/social/", SocialConsumer.as_asgi()),
        ])
    ),
})
