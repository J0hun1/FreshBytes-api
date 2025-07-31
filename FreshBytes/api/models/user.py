from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.exceptions import ValidationError
import uuid

class UserManager(BaseUserManager):
    def create_user(self, user_email, password=None, **extra_fields):
        """Create and save a user with a valid password.

        Security fix: a password **must** be provided. Removes the default
        plaintext password that previously existed.
        """
        if not user_email:
            raise ValueError('The Email field must be set')
        if not password:
            raise ValueError('Password must be provided')

        user_email = self.normalize_email(user_email)
        user = self.model(user_email=user_email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, user_email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(user_email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('seller', 'Seller'),
        ('customer', 'Customer'),
    ]

    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    user_name = models.CharField(max_length=255)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    user_email = models.EmailField(unique=True, null=False, default="")
    password = models.CharField(max_length=128, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    user_phone = models.CharField(max_length=255)
    street = models.CharField(max_length=255, blank=True, null=True)
    barangay = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    province = models.CharField(max_length=255, blank=True, null=True)
    zip_code = models.CharField(max_length=10, blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    terms_accepted = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'user_email'
    REQUIRED_FIELDS = ['user_name', 'first_name', 'last_name']

    def clean(self):
        """Validate that is_active and is_deleted cannot both be True"""
        super().clean()
        if self.is_active and self.is_deleted:
            raise ValidationError({
                'is_active': 'A user cannot be both active and deleted.',
                'is_deleted': 'A user cannot be both active and deleted.'
            })

    def save(self, *args, **kwargs):
        from ..services.users_services import validate_user_role
        
        # Validate the model before saving
        self.clean()
        
        # Ensure user_id is set (UUID will be generated automatically)
        self = validate_user_role(self)
        super().save(*args, **kwargs)

    def soft_delete(self):
        """Soft delete a user by setting is_deleted=True and is_active=False"""
        self.is_deleted = True
        self.is_active = False
        self.save(update_fields=['is_deleted', 'is_active'])

    def restore(self):
        """Restore a soft-deleted user by setting is_deleted=False and is_active=True"""
        self.is_deleted = False
        self.is_active = True
        self.save(update_fields=['is_deleted', 'is_active'])

    def deactivate(self):
        """Deactivate a user without deleting them"""
        self.is_active = False
        self.save(update_fields=['is_active'])

    def activate(self):
        """Activate a user"""
        self.is_active = True
        self.is_deleted = False  # Ensure deleted flag is also cleared
        self.save(update_fields=['is_active', 'is_deleted'])

    # Group-based role checking methods (for new permission system)
    def is_admin(self):
        """Check if user is in Admin group or has admin role"""
        return self.groups.filter(name='Admin').exists() or self.role == 'admin'
    
    def is_seller(self):
        """Check if user is in Seller group or has seller role"""
        return self.groups.filter(name='Seller').exists() or self.role == 'seller'
    
    def is_customer(self):
        """Check if user is in Customer group or has customer role"""
        return self.groups.filter(name='Customer').exists() or self.role == 'customer'
    
    def has_role(self, role_name):
        """Check if user has a specific role (supports both groups and role field)"""
        group_name = role_name.capitalize()
        return (self.groups.filter(name=group_name).exists() or 
                self.role == role_name.lower())
    
    def get_primary_role(self):
        """Get the user's primary role based on group membership (falls back to role field)"""
        if self.groups.filter(name='Admin').exists():
            return 'admin'
        elif self.groups.filter(name='Seller').exists():
            return 'seller'
        elif self.groups.filter(name='Customer').exists():
            return 'customer'
        else:
            # Fallback to role field if no groups assigned
            return self.role
    
    def sync_role_with_groups(self):
        """Sync the role field with group membership (for backward compatibility)"""
        primary_role = self.get_primary_role()
        if self.role != primary_role:
            self.role = primary_role
            self.save(update_fields=['role'])
    
    def assign_to_group(self, group_name):
        """Helper method to assign user to a specific group"""
        from django.contrib.auth.models import Group
        try:
            group = Group.objects.get(name=group_name)
            self.groups.add(group)
            # Update role field to match
            self.role = group_name.lower()
            self.save(update_fields=['role'])
            return True
        except Group.DoesNotExist:
            return False

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        db_table = 'Users'
