"""
ASGI config for Emessage project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter



os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Emessage.settings')

# initializing the ASGI application early to ensure the AppRegistry is populated before importing code that may import ORM models.
django_asgi_app = get_asgi_application()

import Users.routing  # Import the routing module from your users app

application = ProtocolTypeRouter({
    # Django's ASGI application to handle traditional HTTP requests
    "http": django_asgi_app,

    # websocket connections handler
    "websocket": AuthMiddlewareStack(
        URLRouter(
            Users.routing.websocket_urlpatterns  # Import your websocket URL patterns from the users app
        )
    )
})