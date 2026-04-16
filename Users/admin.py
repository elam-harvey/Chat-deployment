from django.contrib import admin

# Register your models here.
from .models import ChatGroup
admin.site.register(ChatGroup)

class ChatGroupAdmin(admin.ModelAdmin):
    # this makes the UUID show up in the list as read only
    list_display = ('name', 'admin', 'id')
    readonly_fields = ('id',)
