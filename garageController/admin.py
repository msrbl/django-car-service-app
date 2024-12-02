from django.contrib import admin
from .models import Vehicle

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'vin', 'make', 'model', 'created_at')
    search_fields = ('vin', 'make', 'model')
    list_filter = ('created_at',)