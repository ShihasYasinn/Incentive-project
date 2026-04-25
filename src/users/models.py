from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, role='employee', **extra_fields):
        if not email:
            raise ValueError("Email is required")

        email = self.normalize_email(email)
        user = self.model(email=email, role=role, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(
            email=email,
            password=password,
            role='admin',
            **extra_fields
        )

class User(AbstractBaseUser, PermissionsMixin):

    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('analyst', 'Data Analyst'),
        ('employee', 'Employee'),
    )

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='employee')
    
    # Employee details (moved from Employee model)
    full_name = models.CharField(max_length=255, blank=True, null=True)
    branch = models.CharField(max_length=100, blank=True, null=True)

    employee_id = models.CharField(
        max_length=50, 
        unique=True, 
        db_index=True, 
        null=True, 
        blank=True
    )


    # Django required fields
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False) 

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.full_name or self.email} ({self.role})"