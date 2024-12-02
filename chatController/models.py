from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()

class Chat(models.Model):
    CHAT_TYPE_CHOICES = [
        ('admin', 'Administrator'),
        ('ai', 'AI')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chats')
    manager = models.ForeignKey(User, on_delete=models.CASCADE, related_name='manager_chats', null=True, blank=True)
    chat_type = models.CharField(max_length=10, choices=CHAT_TYPE_CHOICES)
    created_at = models.DateTimeField(default=timezone.now)

class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)