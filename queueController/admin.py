from django.contrib import admin
from .models import Post, Ticket

class TicketAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'user', 'appointment', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('name', 'user__username')
    ordering = ('-created_at',)

class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'is_occupied', 'ticket')
    list_filter = ('is_occupied',)
    search_fields = ('name',)
    ordering = ('name',)

admin.site.register(Post, PostAdmin)
admin.site.register(Ticket, TicketAdmin)