from django.contrib import admin
from .models import Employee, Branch

@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'created_at')
    search_fields = ('name', 'code')

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'employee_id', 'branch', 'email', 'user', 'is_active')
    list_filter = ('branch', 'is_active')
    search_fields = ('full_name', 'employee_id', 'email')
    readonly_fields = ('user', 'created_at', 'updated_at')
    fieldsets = (
        ('Identification', {
            'fields': ('full_name', 'employee_id', 'email', 'branch', 'user', 'is_active')
        }),
        ('Performance Metrics', {
            'fields': ('total_earning', 'free_service_count', 'paid_service_count', 'rr_service_count', 'wheel_alignment_lathe')
        }),
        ('System Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
