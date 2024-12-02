from django.contrib import admin
from .models import Service, Work

class WorkInline(admin.TabularInline):
    model = Work
    extra = 1

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price', 'created_at')
    search_fields = ('name',)
    list_filter = ('created_at',)
    inlines = [WorkInline]
