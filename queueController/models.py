from django.db import models
from django.conf import settings

from appointmentController.models import Appointment

class Ticket(models.Model):
    STATUS_CHOICES = [
        ('queued', 'Queued'),
        ('in_service', 'In Service'),
        ('completed', 'Completed'),
    ]
    name = models.CharField(max_length=50)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='queued')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Ticket {self.id} - {self.status}'


class Post(models.Model):
    name = models.CharField(max_length=50)
    is_occupied = models.BooleanField(default=False)
    ticket = models.ForeignKey(Ticket, on_delete = models.SET_NULL, null = True, blank = True)

    def __str__(self):
        return self.name
