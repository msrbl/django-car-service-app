from django.contrib import admin
from .models import Chat, Message

@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'manager', 'chat_type', 'created_at')
    search_fields = ('user__username', 'manager__username', 'chat_type')
    list_filter = ('chat_type', 'created_at')
    date_hierarchy = 'created_at'

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'chat', 'sender', 'text', 'timestamp')
    search_fields = ('chat__id', 'sender__username', 'text')
    list_filter = ('timestamp',)
    date_hierarchy = 'timestamp'
