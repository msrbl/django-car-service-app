from django.db import models

class Service(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Work(models.Model):
    service = models.ForeignKey(Service, related_name='works', on_delete=models.CASCADE)
    description = models.TextField()

    def __str__(self):
        return self.description
