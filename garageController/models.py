from django.db import models
from django.conf import settings

class Vehicle(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='vehicles')
    vin = models.CharField(max_length=17, unique=True, null=True)
    make = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.make} {self.model} ({self.vin})"
