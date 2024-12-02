from django.conf import settings
from django.db import models
from django.contrib.auth.models import User

class UserNotificationToken(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    fcm_token = models.CharField(max_length=255)
    
    def __str__(self):
        return self.user.username