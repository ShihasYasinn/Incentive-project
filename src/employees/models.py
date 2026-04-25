from django.db import models
from django.conf import settings

class UploadSession(models.Model):
    """
    Tracks every Excel upload session for audit and history.
    """
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='upload_sessions'
    )
    file_name = models.CharField(max_length=255)
    report_date = models.DateField(help_text="The date this data belongs to.")
    upload_timestamp = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(
        default=True, 
        help_text="Only the latest upload for a specific date should be active."
    )

    class Meta:
        ordering = ['-upload_timestamp']

    def __str__(self):
        return f"Upload for {self.report_date} by {self.uploaded_by} ({self.upload_timestamp.strftime('%Y-%m-%d %H:%M')})"



class PerformanceRecord(models.Model):
    """
    Stores daily performance data for employees uploaded via Excel.
    """
    upload_session = models.ForeignKey(
        UploadSession,
        on_delete=models.CASCADE,
        related_name='records',
        null=True, # Null for legacy data
        blank=True
    )
    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='performance_records',
        help_text="The employee this data belongs to."
    )
    date = models.DateField(
        help_text="The date this performance data refers to."
    )
    
    # Productivity metrics
    free = models.IntegerField(
        default=0,
        help_text="Number of free services"
    )
    paid = models.IntegerField(
        default=0,
        help_text="Number of paid services"
    )
    rr = models.IntegerField(
        default=0,
        help_text="Number of RR (Return/Repair) services"
    )
    vehicle_count = models.IntegerField(
        default=0,
        help_text="Total services (Free + Paid + RR)"
    )

    def save(self, *args, **kwargs):
        # Auto-calculate vehicle count
        self.vehicle_count = (self.free or 0) + (self.paid or 0) + (self.rr or 0)
        super().save(*args, **kwargs)
    
    # Other work metrics
    wheel_alignment_lathe = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00,
        verbose_name="Wheel Alignment / Lathe",
        help_text="Amount for wheel alignment or lathe tasks"
    )

    leave_status = models.CharField(
        max_length=10,
        default='P',
        choices=[('P', 'Present'), ('L', 'Leave')],
        help_text="Attendance status from Labor Report (P/L)"
    )
    
    total_earnings = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00,
        verbose_name="Gross Earnings",
        help_text="Total earnings for the period (Gross)"
    )
    
    actual_earnings = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00,
        verbose_name="Net Earnings",
        help_text="Actual earnings after deductions (Wheel Alignment + Service Deductions)"
    )

    is_above_150 = models.BooleanField(
        default=False,
        help_text="Set to True if BS Load is Above 150, False if Below 150 (Uploaded as Yes/No)"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', 'employee']
        # We remove unique_together to allow keeping history of re-uploads
        # Unique constraints are now handled via the 'is_active' flag in UploadSession
        verbose_name = 'Performance Record'
        verbose_name_plural = 'Performance Records'

    def __str__(self):
        return f"{self.employee.full_name or self.employee.email} - {self.date}"

    @property
    def total_load(self):
        return self.free + self.paid + self.rr


class MonthlyTarget(models.Model):
    """
    Sets the monthly target amount for all employees.
    """
    month = models.DateField(unique=True, help_text="The first day of the month this target applies to.")
    target_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Monthly Target"
        verbose_name_plural = "Monthly Targets"

    def __str__(self):
        return f"{self.month.strftime('%B %Y')}: {self.target_amount}"


class IncentiveSlab(models.Model):
    """
    Defines the incentive percentage based on achievement level.
    3 Fields: Slab Type, Achievement %, and Incentive %.
    """
    SLAB_CHOICES = [
        ('ABOVE', 'Above 150'),
        ('BELOW', 'Below 150'),
        ('BOTH', 'Both'),
    ]
    
    load_slab = models.CharField(
        max_length=10, 
        choices=SLAB_CHOICES, 
        default='BELOW',
        help_text="Above 150 or Below 150"
    )
    min_achievement_percent = models.DecimalField(
        max_digits=6, 
        decimal_places=2, 
        help_text="Minimum achievement percentage (e.g., 80)"
    )
    max_achievement_percent = models.DecimalField(
        max_digits=6, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Optional maximum achievement percentage (e.g., 89 for 80-89% range)"
    )
    incentive_percent = models.DecimalField(
        max_digits=6, 
        decimal_places=2, 
        help_text="Incentive percentage (e.g., 2 for 2% of target amount)"
    )

    class Meta:
        ordering = ['load_slab', '-min_achievement_percent']
        verbose_name = "Incentive Slab"
        verbose_name_plural = "Incentive Slabs"

    def __str__(self):
        range_str = f"{self.min_achievement_percent}"
        if self.max_achievement_percent:
            range_str += f"-{self.max_achievement_percent}%"
        else:
            range_str += "%+"
        return f"{self.get_load_slab_display()}: {range_str} Achieved -> {self.incentive_percent}% Incentive"


class MonthlyIncentive(models.Model):
    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='incentives'
    )
    month = models.DateField(help_text="The first day of the month for this calculation.")
    total_earnings = models.DecimalField(max_digits=12, decimal_places=2)
    target_amount = models.DecimalField(max_digits=12, decimal_places=2)
    achievement_percent = models.DecimalField(max_digits=6, decimal_places=2)
    total_vehicles = models.IntegerField(default=0)
    incentive_percent = models.DecimalField(max_digits=6, decimal_places=2)
    efficiency_bonus = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    incentive_amount = models.DecimalField(max_digits=12, decimal_places=2)
    slab_type = models.CharField(max_length=10) # ABOVE, BELOW, BOTH
    
    calculated_at = models.DateTimeField(auto_now=True)

    @property
    def base_incentive(self):
        return self.incentive_amount - self.efficiency_bonus

    class Meta:
        unique_together = ['employee', 'month']
        verbose_name = "Monthly Incentive"
        verbose_name_plural = "Monthly Incentives"

    def __str__(self):
        return f"{self.employee.full_name or self.employee.email} - {self.month.strftime('%B %Y')}: ₹{self.incentive_amount}"


class LoadGrowthSlab(models.Model):
    """
    Defines unique slabs for LOAD GROWTH incentives.
    Admin can configure bonuses for growth and deductions for degrowth.
    """
    SLAB_CHOICES = [
        ('ABOVE', 'Above 150'),
        ('BELOW', 'Below 150'),
        ('BOTH', 'Both'),
    ]
    
    load_slab = models.CharField(
        max_length=10, 
        choices=SLAB_CHOICES, 
        default='BOTH',
        help_text="Above 150, Below 150, or Both"
    )
    min_growth_percent = models.DecimalField(
        max_digits=6, 
        decimal_places=2, 
        null=True,
        blank=True,
        help_text="Minimum growth percentage (e.g., 5.00 for 5%)"
    )
    max_growth_percent = models.DecimalField(
        max_digits=6, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Maximum growth percentage (e.g., 9.99)"
    )
    incentive_amount = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=0.00,
        help_text="Fixed bonus amount for this growth tier"
    )
    deduction_percent = models.DecimalField(
        max_digits=6, 
        decimal_places=2, 
        default=0.00,
        help_text="Percentage deduction from eligible incentive (used for degrowth, e.g., 15)"
    )

    class Meta:
        ordering = ['load_slab', '-min_growth_percent']
        verbose_name = "Load Growth Slab"
        verbose_name_plural = "Load Growth Slabs"

    def __str__(self):
        range_str = ""
        if self.min_growth_percent is not None and self.max_growth_percent is not None:
            range_str = f"{self.min_growth_percent}% to {self.max_growth_percent}%"
        elif self.min_growth_percent is not None:
            range_str = f"{self.min_growth_percent}%+"
        elif self.max_growth_percent is not None:
            range_str = f"Up to {self.max_growth_percent}%"
        
        type_str = "Bonus" if self.incentive_amount > 0 else "Deduction"
        val_str = f"₹{self.incentive_amount}" if self.incentive_amount > 0 else f"{self.deduction_percent}%"
        
        return f"{self.get_load_slab_display()} | Growth: {range_str} -> {type_str}: {val_str}"


