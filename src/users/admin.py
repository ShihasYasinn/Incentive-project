from django.contrib import admin
from .models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'full_name', 'employee_id', 'role', 'branch', 'is_staff', 'is_active')
    search_fields = ('email', 'full_name', 'employee_id')
    list_filter = ('role', 'branch', 'is_staff', 'is_active')
    
    fieldsets = (
        ('Authentication', {
            'fields': ('email', 'password')
        }),
        ('Personal Info', {
            'fields': ('full_name', 'role', 'branch', 'employee_id')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Important Dates', {
            'fields': ('last_login', 'created_at', 'updated_at')
        }),
    )
    readonly_fields = ('created_at', 'updated_at')
