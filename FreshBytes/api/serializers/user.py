from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from django.core.validators import EmailValidator
from django.core.exceptions import ValidationError
import re
from ..models import User

class UserListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for user lists"""
    full_name = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()
    role_display = serializers.SerializerMethodField()
    created_date = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'user_id', 'user_name', 'full_name', 'user_email', 'role', 'role_display',
            'is_active', 'is_deleted', 'status_display', 'created_at', 'created_date',
            'is_staff', 'is_superuser', 'terms_accepted', 'phone_verified', 'email_verified'
        ]
        read_only_fields = ['user_id', 'created_at', 'full_name', 'status_display', 'role_display', 'created_date']

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()

    def get_status_display(self, obj):
        if obj.is_deleted:
            return "Deleted"
        elif not obj.is_active:
            return "Inactive"
        else:
            return "Active"

    def get_role_display(self, obj):
        role_mapping = {
            'admin': 'Administrator',
            'seller': 'Seller',
            'customer': 'Customer'
        }
        return role_mapping.get(obj.role, obj.role.title())

    def get_created_date(self, obj):
        return obj.created_at.strftime("%Y-%m-%d") if obj.created_at else None

class UserSerializer(serializers.ModelSerializer):
    # Password is optional for updates, required for user creation.
    password = serializers.CharField(write_only=True, required=False, allow_blank=False)
    full_name = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()
    role_display = serializers.SerializerMethodField()
    created_date = serializers.SerializerMethodField()
    updated_date = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['user_id', 'user_name', 'first_name', 'last_name', 'full_name', 'user_email', 
                 'password', 'user_phone', 'street', 'barangay', 'city', 'province', 'zip_code','role', 'role_display', 'created_at', 'updated_at', 'created_date', 'updated_date', 'is_active', 'is_deleted', 
                 'is_staff', 'is_superuser', 'terms_accepted', 'phone_verified', 'email_verified', 'status_display']
        read_only_fields = ['user_id', 'created_at', 'updated_at', 'full_name', 'status_display', 'role_display', 'created_date', 'updated_date']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()

    def get_status_display(self, obj):
        if obj.is_deleted:
            return "Deleted"
        elif not obj.is_active:
            return "Inactive"
        else:
            return "Active"

    def get_role_display(self, obj):
        role_mapping = {
            'admin': 'Administrator',
            'seller': 'Seller',
            'customer': 'Customer'
        }
        return role_mapping.get(obj.role, obj.role.title())

    def get_created_date(self, obj):
        return obj.created_at.strftime("%Y-%m-%d") if obj.created_at else None

    def get_updated_date(self, obj):
        return obj.updated_at.strftime("%Y-%m-%d") if obj.updated_at else None

    def validate_user_name(self, value):
        """Validate username format and uniqueness"""
        if not value:
            raise serializers.ValidationError("Username is required.")
        
        # Check length
        if len(value) < 3:
            raise serializers.ValidationError("Username must be at least 3 characters long.")
        
        if len(value) > 50:
            raise serializers.ValidationError("Username must be no more than 50 characters long.")
        
        # Check for valid characters (alphanumeric and underscore only)
        if not re.match(r'^[a-zA-Z0-9_]+$', value):
            raise serializers.ValidationError("Username can only contain letters, numbers, and underscores.")
        
        # Check uniqueness (excluding current instance for updates)
        if self.instance:
            if User.objects.filter(user_name=value).exclude(pk=self.instance.pk).exists():
                raise serializers.ValidationError("This username is already taken.")
        else:
            if User.objects.filter(user_name=value).exists():
                raise serializers.ValidationError("This username is already taken.")
        
        return value

    def validate_user_email(self, value):
        """Validate email format and uniqueness"""
        if not value:
            raise serializers.ValidationError("Email is required.")
        
        # Use Django's built-in email validator
        email_validator = EmailValidator()
        try:
            email_validator(value)
        except ValidationError:
            raise serializers.ValidationError("Please enter a valid email address.")
        
        # Check uniqueness (excluding current instance for updates)
        if self.instance:
            if User.objects.filter(user_email=value).exclude(pk=self.instance.pk).exists():
                raise serializers.ValidationError("This email is already registered.")
        else:
            if User.objects.filter(user_email=value).exists():
                raise serializers.ValidationError("This email is already registered.")
        
        return value.lower()  # Normalize email to lowercase

    def validate_password(self, value):
        """Validate password strength"""
        if not value:
            return value  # Allow empty for updates
        
        # # Check minimum length
        # if len(value) < 8:
        #     raise serializers.ValidationError("Password must be at least 8 characters long.")
        
        # # Check for complexity requirements
        # if not re.search(r'[A-Z]', value):
        #     raise serializers.ValidationError("Password must contain at least one uppercase letter.")
        
        # if not re.search(r'[a-z]', value):
        #     raise serializers.ValidationError("Password must contain at least one lowercase letter.")
        
        # if not re.search(r'\d', value):
        #     raise serializers.ValidationError("Password must contain at least one number.")
        
        # if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
        #     raise serializers.ValidationError("Password must contain at least one special character.")
        
        # # Check for common weak passwords
        # weak_passwords = ['password', '123456', 'qwerty', 'admin', 'user']
        # if value.lower() in weak_passwords:
        #     raise serializers.ValidationError("Please choose a stronger password.")
        
        return value

    def validate_user_phone(self, value):
        """Validate phone number format"""
        if not value:
            raise serializers.ValidationError("Phone number is required.")
        
        # Remove all non-digit characters for validation
        digits_only = re.sub(r'\D', '', value)
        
        # Check if it's a valid Philippine phone number
        if len(digits_only) < 10 or len(digits_only) > 11:
            raise serializers.ValidationError("Please enter a valid Philippine phone number.")
        
        # Check if it starts with valid Philippine prefixes
        valid_prefixes = ['09', '08', '07', '02', '03', '04', '05', '06']
        if not any(digits_only.startswith(prefix) for prefix in valid_prefixes):
            raise serializers.ValidationError("Please enter a valid Philippine phone number.")
        
        return value

    def validate_first_name(self, value):
        """Validate first name"""
        if not value:
            raise serializers.ValidationError("First name is required.")
        
        if len(value) < 2:
            raise serializers.ValidationError("First name must be at least 2 characters long.")
        
        if len(value) > 50:
            raise serializers.ValidationError("First name must be no more than 50 characters long.")
        
        # Check for valid characters (letters, spaces, hyphens, apostrophes)
        if not re.match(r'^[a-zA-Z\s\'-]+$', value):
            raise serializers.ValidationError("First name can only contain letters, spaces, hyphens, and apostrophes.")
        
        return value.strip()

    def validate_last_name(self, value):
        """Validate last name"""
        if not value:
            raise serializers.ValidationError("Last name is required.")
        
        if len(value) < 2:
            raise serializers.ValidationError("Last name must be at least 2 characters long.")
        
        if len(value) > 50:
            raise serializers.ValidationError("Last name must be no more than 50 characters long.")
        
        # Check for valid characters (letters, spaces, hyphens, apostrophes)
        if not re.match(r'^[a-zA-Z\s\'-]+$', value):
            raise serializers.ValidationError("Last name can only contain letters, spaces, hyphens, and apostrophes.")
        
        return value.strip()

    def validate_zip_code(self, value):
        """Validate zip code format"""
        if not value:
            return value  # Optional field
        
        # Check if it's a valid Philippine zip code (4 digits)
        if not re.match(r'^\d{4}$', value):
            raise serializers.ValidationError("Please enter a valid 4-digit zip code.")
        
        return value

    def validate_role(self, value):
        """Validate role assignment"""
        request = self.context.get('request')
        
        # Only allow superusers to change the role
        if request and request.user and not request.user.is_superuser:
            # If updating and trying to change the role
            if self.instance and value != self.instance.role:
                raise serializers.ValidationError("You do not have permission to change roles.")
            # If creating and trying to set a role other than default
            if not self.instance and value != 'customer':
                raise serializers.ValidationError("You do not have permission to assign this role.")
        
        # Validate role value
        valid_roles = ['admin', 'seller', 'customer']
        if value not in valid_roles:
            raise serializers.ValidationError(f"Invalid role. Must be one of: {', '.join(valid_roles)}")
        
        return value

    def validate(self, attrs):
        """Comprehensive validation for user creation and updates"""
        # Check if this is a new user creation
        is_creation = self.instance is None
        
        if is_creation:
            # Password is required for new users
            if not attrs.get('password'):
                raise serializers.ValidationError({"password": "Password is required for new users."})
            
            # Terms must be accepted for new users
            if not attrs.get('terms_accepted', False):
                raise serializers.ValidationError({"terms_accepted": "You must accept the terms to create an account."})
            
            # Set default role to customer for new users
            if not attrs.get('role'):
                attrs['role'] = 'customer'
        
        # Business rule: Sellers must have verified email
        if attrs.get('role') == 'seller':
            if not attrs.get('email_verified', False):
                raise serializers.ValidationError({"email_verified": "Sellers must have a verified email address."})
            
            if not attrs.get('user_email'):
                raise serializers.ValidationError({"user_email": "Sellers must have an email address."})
        
        # Business rule: Admins must have verified email and phone
        if attrs.get('role') == 'admin':
            if not attrs.get('email_verified', False):
                raise serializers.ValidationError({"email_verified": "Administrators must have a verified email address."})
            
            if not attrs.get('phone_verified', False):
                raise serializers.ValidationError({"phone_verified": "Administrators must have a verified phone number."})
        
        # Validate address fields if provided
        address_fields = ['street', 'barangay', 'city', 'province']
        provided_address_fields = [field for field in address_fields if attrs.get(field)]
        
        if provided_address_fields:
            # If any address field is provided, require all basic address fields
            if not attrs.get('street'):
                raise serializers.ValidationError({"street": "Street address is required when providing address information."})
            
            if not attrs.get('city'):
                raise serializers.ValidationError({"city": "City is required when providing address information."})
        
        return super().validate(attrs)

    def create(self, validated_data):
        """Create user with enhanced validation"""
        # Only allow 'customer' or 'seller' roles via public registration
        allowed_roles = ['customer', 'seller']
        requested_role = validated_data.get('role', 'customer')
        if requested_role not in allowed_roles:
            validated_data['role'] = 'customer'
        
        # Hash password
        validated_data['password'] = make_password(validated_data.get('password'))
        
        # Create user
        user = super().create(validated_data)
        
        # Log user creation for audit
        print(f"New user created: {user.user_email} with role: {user.role}")
        
        return user

    def update(self, instance, validated_data):
        """Update user with enhanced validation"""
        # Hash password if provided
        if 'password' in validated_data:
            validated_data['password'] = make_password(validated_data.get('password'))
        
        # Update user
        user = super().update(instance, validated_data)
        
        # Log user update for audit
        print(f"User updated: {user.user_email}")
        
        return user
