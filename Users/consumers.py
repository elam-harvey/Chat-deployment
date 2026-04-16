import json
import uuid
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer 
from .models import ChatGroup, User, Message

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope.get('user')
        self.group_id = self.scope['url_route']['kwargs'].get('group_id')
        self.room_group_name = f'chat_{self.group_id}'
        self.username = self.user.username if self.user else None

        print(f"WebSocket connect attempt: user={self.user}, is_authenticated={self.user.is_authenticated if self.user else 'N/A'}, group_id={self.group_id} (type: {type(self.group_id)})")

        # 1. Reject immediately if they aren't logged in (Guest)
        if not self.user or not self.user.is_authenticated:
            print("Connection rejected: user not authenticated")
            await self.close()
            return

        # 2. Check if they are actually a member in the DB
        is_member = await self.is_member()
        print(f"User {self.user.username} is_member check: {is_member}")
        if not is_member:
            print(f"Connection rejected: user {self.user.username} is not a member of group {self.group_id}")
            await self.close()
            return

        # 3. If they passed those checks, let them in!
        print(f"Connection accepted: user {self.user.username} joining group {self.group_id}")
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        
        # Broadcast that they joined (Optional)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_joined',
                'username': self.user.username,
            }
        )
    async def disconnect(self, close_code):
        # This happens when a user disconnects from the websocket
        # Leave the room group
        print(f"WebSocket disconnect: user={self.username}, group={self.group_id}, code={close_code}")
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        print(f"Connection closed: {self.channel_name}")
        print(f"{self.username} - has left the chat")

    async def receive(self, text_data):
        # This happens when the users send message from their browser
        data = json.loads(text_data)
        message_type = data.get('type', 'chat_message')
        
        if message_type == 'chat_message':
            await self.handle_chat_message(data)
        elif message_type == 'join_group':
            await self.handle_join_group()
        else:
            # Handle unknown message types
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': f'Unknown message type: {message_type}'
            }))

    async def handle_join_group(self):
        # Handle user joining the group
        if not self.user or not self.user.is_authenticated:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'reason': 'authentication_required',
                'message': 'You must be authenticated to join this group.'
            }))
            return

        if await self.is_member():
            await self.send(text_data=json.dumps({
                'type': 'join_status',
                'status': 'already_member',
                'message': 'You are already a member of this group.'
            }))
            return

        # Add user to group
        if await self.add_user_to_group():
            await self.send(text_data=json.dumps({
                'type': 'join_status',
                'status': 'success',
                'message': f'Welcome to the group, {self.username}! You can now send messages.'
            }))
            # Notify group that user joined
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_joined',
                    'username': self.username
                }
            )
        else:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'reason': 'join_failed',
                'message': 'Failed to join the group. Please try again.'
            }))

    async def handle_chat_message(self, data):
        # Check if user is a member before allowing message
        if not self.user or not self.user.is_authenticated:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'reason': 'authentication_required',
                'message': 'You must be authenticated to send messages.'
            }))
            return

        if not await self.is_member():
            await self.send(text_data=json.dumps({
                'type': 'error',
                'reason': 'not_member',
                'message': 'You must join the group first to send messages. Send a "join_group" message to join.'
            }))
            return

        message = data.get('message', '').strip()
        
        if not message:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Message cannot be empty.'
            }))
            return

        # Save message to database
        await self.save_group_message(message)

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': self.username
            }
        )

    async def user_joined(self, event):
        # Receive user joined event from room group
        await self.send(text_data=json.dumps({
            'type': 'user_joined',
            'message': f'{event["username"]} has joined the group.'
        }))

    async def chat_message(self, event):
        # receive chat message from room group
        print(f"chat_message event received: {event}")
        try:
            message = event.get('message', '')
            username = event.get('username', 'System')
        except Exception:
            message = event['message'] if 'message' in event else ''
            username = event['username'] if 'username' in event else 'System'

        # send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': message,
            'username': username
        }))

    # listen for an event where the user is kicked out by the admin
    async def user_kicked(self, event):
        user_id = event['user_id']

        # if the current connection matches the the ID, close it!
        if str(self.user.id)== str(user_id):
            await self.send(text_data=json.dumps({
                'type': 'kicked',
                'message': 'You have been removed from the group by the admin.'
            }))
            await self.close()

    @database_sync_to_async
    def is_member(self):
        """Check if the current user is a member of the group"""
        try:
            print(f"is_member check: group_id={self.group_id} (type: {type(self.group_id)}), user_id={self.user.id}")
            group = ChatGroup.objects.get(id=self.group_id)
            print(f"Found group: {group.name} with {group.members.count()} members")
            members = list(group.members.all().values_list('username', flat=True))
            print(f"Group members: {members}")
            is_member = group.members.filter(id=self.user.id).exists()
            print(f"is_member check: group={group.id}, user={self.user.id} ({self.user.username}), is_member={is_member}")
            return is_member
        except ChatGroup.DoesNotExist:
            print(f"is_member check: group {self.group_id} does not exist")
            return False
        except Exception as e:
            print(f"is_member check: error {e}")
            return False

    @database_sync_to_async
    def add_user_to_group(self):
        """Add the current user to the group"""
        try:
            group = ChatGroup.objects.get(id=self.group_id)
            group.members.add(self.user)
            return True
        except ChatGroup.DoesNotExist:
            return False

    @database_sync_to_async
    def save_group_message(self, content):
        """Save a group message to the database"""
        from .models import GroupMessage
        try:
            group = ChatGroup.objects.get(id=self.group_id)
            GroupMessage.objects.create(
                group=group,
                sender=self.user,
                content=content
            )
        except ChatGroup.DoesNotExist:
            pass


class DirectChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope.get('user')
        self.other_user_id = int(self.scope['url_route']['kwargs'].get('other_user_id'))
        self.other_user = await self.get_user(self.other_user_id)
        self.room_group_name = self.get_room_group_name()

        print(f"DM connect attempt: user={self.user}, other_user={self.other_user}, auth={self.user.is_authenticated if self.user else 'N/A'}")

        if not self.user or not self.user.is_authenticated or not self.other_user:
            await self.close()
            return

        if self.other_user == self.user:
            await self.close()
            return

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type', 'chat_message')

        if message_type != 'chat_message':
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': f'Unknown message type: {message_type}'
            }))
            return

        message = data.get('message', '').strip()
        if not message:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Message cannot be empty.'
            }))
            return

        await self.save_direct_message(message)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'direct_chat_message',
                'message': message,
                'username': self.user.username,
                'sender_id': self.user.id
            }
        )

    async def direct_chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message'],
            'username': event['username'],
            'sender_id': event['sender_id']
        }))

    def get_room_group_name(self):
        ids = sorted([str(self.user.id), str(self.other_user_id)])
        return f'direct_{ids[0]}_{ids[1]}'

    @database_sync_to_async
    def get_user(self, user_id):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None

    @database_sync_to_async
    def save_direct_message(self, content):
        Message.objects.create(
            sender=self.user,
            receiver=self.other_user,
            content=content
        )

class PresenceConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope.get('user')
        if self.scope['user'].is_anonymous:
            await self.close()
        else:
            await self.accept()
            await self.set_user_online()
    async def disconnect(self, close_code):
        await self.set_user_offline()
    @database_sync_to_async
    def set_user_online(self):
        self.user.is_online = True
        self.user.save()
    @database_sync_to_async
    def set_user_offline(self):
        self.user.is_online = False
        self.user.save()