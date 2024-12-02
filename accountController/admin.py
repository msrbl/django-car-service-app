from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


class UserAdmin(UserAdmin):
    model = User
    list_display = ('phone', 'first_name', 'last_name', 'is_active',)
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    fieldsets = (
        (None, {'fields': ('phone', 'first_name', 'last_name', 'password')}),
        ('Permissions', {'fields': ('is_active', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'phone', 'first_name', 'last_name', 'password1', 'password2',  
                'is_active', 'groups', 'user_permissions'
            )}
        ),
    )
    search_fields = ('phone', 'first_name', 'last_name')
    ordering = ('phone',)
    filter_horizontal = ('groups', 'user_permissions',)

admin.site.register(User, UserAdmin)