from django.contrib import admin
from .models import CarMake, CarModel, Appointment

@admin.register(CarMake)
class CarMakeAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(CarModel)
class CarModelAdmin(admin.ModelAdmin):
    list_display = ['make', 'name']
    search_fields = ['make__name', 'name']
    list_filter = ['make']

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'time', 'make', 'model']
    search_fields = ['user__username', 'make__name', 'model__name']
    list_filter = ['date', 'make']