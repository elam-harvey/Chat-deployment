from django.db import models
from django.conf import settings
import uuid
from django.contrib.auth.models import AbstractUser

# Create your models here.
class ChatGroup(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='chat_groups')
    users_online = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='online_in_groups', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    admin = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='admin_groups')

    def __str__(self):
        return self.name
    
    # a function to generate the invite link for the group
    def get_invite_link(self):
        from django.urls import reverse
        return reverse('join_group', args=[str(self.id)])
    
class User(AbstractUser):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)
    phone_no = models.CharField(max_length=15, blank=False, null=False)
    profile_pic = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    about = models.CharField(max_length=255, default ="Hello Am on Emessage", blank=True, null=True)
    is_online = models.BooleanField(default=False)
    last_seen = models.DateTimeField(null=True, blank=True)
    share_presence = models.BooleanField(default=True)

    def __str__(self):
        return self.username

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Message from {self.sender} to {self.receiver}: {self.content[:20]}"

class GroupMessage(models.Model):
    group = models.ForeignKey(ChatGroup, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message in {self.group.name} by {self.sender}: {self.content[:20]}"
    
