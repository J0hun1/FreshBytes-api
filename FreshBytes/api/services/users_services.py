from django.utils import timezone
from django.core.exceptions import ValidationError

def generate_user_id(last_user):
    """Generate unique user ID"""
    current_year = timezone.now().year % 100
    if last_user:
        last_id = int(last_user.user_id[3:6])
        return f"uid{last_id + 1:03d}{current_year:02d}"
    return f"uid001{current_year:02d}"

def validate_user_role(user):
    """Validate user role and permissions"""
    if user.role == 'seller' and not user.user_email:
        raise ValidationError('Sellers must have an email address')
    
    # Set admin permissions
    if user.role == 'admin':
        user.is_staff = True
        user.is_superuser = True
    
    return user

def set_default_password(user, password):
    """Set user password with proper handling"""
    if password:
        user.set_password(password)
    else:
        user.set_password('defaultpassword123')
