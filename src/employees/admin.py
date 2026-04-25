from django.contrib import admin

from employees.models import PerformanceRecord, MonthlyTarget, IncentiveSlab, MonthlyIncentive, LoadGrowthSlab

@admin.register(PerformanceRecord)
class PerformanceRecordAdmin(admin.ModelAdmin):
    list_display = (
        'employee', 
        'date', 
        'free', 
        'paid', 
        'rr', 
        'wheel_alignment_lathe', 
        'leave_status',
        'total_earnings', 
        'actual_earnings',
        'is_above_150',
        'created_at'
    )
    list_filter = ('date', 'leave_status', 'employee__branch', 'employee__role')
    search_fields = ('employee__email', 'employee__full_name', 'employee__employee_id')
    date_hierarchy = 'date'
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Employee Information', {
            'fields': ('employee', 'date', 'leave_status')
        }),
        ('Productivity Metrics', {
            'fields': ('free', 'paid', 'rr')
        }),
        ('Other Work', {
            'fields': ('wheel_alignment_lathe',)
        }),
        ('Financials', {
            'fields': ('total_earnings', 'actual_earnings', 'is_above_150')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(MonthlyTarget)
class MonthlyTargetAdmin(admin.ModelAdmin):
    list_display = ('month', 'target_amount')
    list_filter = ('month',)

@admin.register(IncentiveSlab)
class IncentiveSlabAdmin(admin.ModelAdmin):
    list_display = ('load_slab', 'min_achievement_percent', 'max_achievement_percent', 'incentive_percent')
    list_filter = ('load_slab',)

@admin.register(LoadGrowthSlab)
class LoadGrowthSlabAdmin(admin.ModelAdmin):
    list_display = ('load_slab', 'min_growth_percent', 'max_growth_percent', 'incentive_amount', 'deduction_percent')
    list_filter = ('load_slab',)

@admin.register(MonthlyIncentive)
class MonthlyIncentiveAdmin(admin.ModelAdmin):
    list_display = ('employee', 'month', 'total_earnings', 'target_amount', 'achievement_percent', 'incentive_amount')
    list_filter = ('month', 'slab_type')
    search_fields = ('employee__full_name', 'employee__employee_id')
    readonly_fields = ('calculated_at',)
