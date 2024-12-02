from django.db import models
from django.conf import settings

from premierSearchController.models import Service

class CarMake(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class CarModel(models.Model):
    make = models.ForeignKey(CarMake, on_delete=models.CASCADE, related_name='models')
    name = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.make.name} {self.name}"

class Appointment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='appointments')
    make = models.CharField(max_length=50, null=True, blank=True)
    model = models.CharField(max_length=50, null=True, blank=True)
    date = models.DateField()
    time = models.TimeField()
    comment = models.TextField(blank=True, null=True)
    services = models.ManyToManyField(Service)
    is_live_queue = models.BooleanField(default=False)
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return f"Appointment for {self.user} on {self.date} at {self.time}"
    
    def complete_appointment(self):
        self.is_completed = True
        self.save()

    @classmethod
    def get_next_in_queue(cls):
        return cls.objects.filter(is_live_queue=True, is_completed=False).order_by('date', 'time').first()
