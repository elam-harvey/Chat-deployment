# users/routing.py

from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # We use re_path since websockets often need flexble URL patterns, and we want to capture the username from the URL
    # the group_id part makes the url dynamic, allowing us to have different groups
    re_path(r'^ws/chat/(?P<group_id>[\w-]+)/$', consumers.ChatConsumer.as_asgi()),
    # direct message websocket URL
    re_path(r'^ws/dm/(?P<other_user_id>\d+)/$', consumers.DirectChatConsumer.as_asgi()),
    # presence websocket URL for tracking online status
    re_path(r'^ws/presence/$', consumers.PresenceConsumer.as_asgi()),
]