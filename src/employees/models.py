from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

class Branch(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Branches"
        ordering = ['name']

class Employee(models.Model):
    """
    Model to store Employee details and performance metrics for incentive calculations.
    Designed to be scalable and indexed for fast retrieval.
    """
    
    # User Account Link
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='employee_profile',
        null=True, blank=True,
        help_text="Linked user account"
    )

    # Identity Information
    full_name = models.CharField(
        max_length=255, 
        help_text="Full name of the employee as per records"
    )
    email = models.EmailField(
        unique=True,
        null=True,
        blank=True,
        help_text="Email address for the user account"
    )
    branch = models.ForeignKey(
        Branch,
        on_delete=models.PROTECT,
        related_name='employees',
        help_text="Branch where the employee is stationed"
    )
    employee_id = models.CharField(
        max_length=50, 
        unique=True, 
        db_index=True,
        help_text="Unique employee identification number"
    )

    # Performance & Earning Metrics (Based on provided reports)
    total_earning = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=0.00,
        help_text="Total earnings for the period"
    )
    
    # Service Counts
    free_service_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of FREE services completed"
    )
    paid_service_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of PAID services completed"
    )
    rr_service_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of RR services completed"
    )
    
    # Other Work
    wheel_alignment_lathe = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=0.00,
        help_text="Earnings or metrics from Wheel Alignment/Lathe work"
    )

    # System Fields for Scalability & Security
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this employee record is active"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Employee"
        verbose_name_plural = "Employees"
        ordering = ['full_name']
        indexes = [
            models.Index(fields=['employee_id', 'branch']),
        ]

    def save(self, *args, **kwargs):
        if not self.user and self.email:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            # Create user if it doesn't exist
            if not User.objects.filter(email=self.email).exists():
                new_user = User.objects.create_user(
                    email=self.email,
                    role='employee',
                    password=self.employee_id # Default password is their Employee ID
                )
                self.user = new_user
            else:
                # If user already exists with this email, link it
                self.user = User.objects.get(email=self.email)
        
        # Ensure name stays in sync or other logic
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.full_name} ({self.employee_id}) - {self.branch}"
