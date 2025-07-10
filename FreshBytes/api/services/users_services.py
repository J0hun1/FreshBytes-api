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
    """Ensure role ↔ permissions consistency.

    Rules:
    1. If `is_superuser` is True → force role to "admin" and `is_staff` True.
    2. If role is "admin" but `is_superuser` was set to False → demote role to "customer" and clear staff/superuser flags.
    3. For non-admin roles, ensure `is_staff` and `is_superuser` are False.
    4. Sellers must still have an email address.
    """

    # Business validation
    if user.role == 'seller' and not user.user_email:
        raise ValidationError('Sellers must have an email address')

    # --- Synchronise role and permission flags ---

    if user.is_superuser:
        # Promotion: make sure everything else is in sync
        user.role = 'admin'
        user.is_staff = True
    else:
        # No longer a superuser.
        if user.role == 'admin':
            # Demote to customer when super privileges revoked
            user.role = 'customer'
        # Regardless of old role, ensure staff/superuser flags are cleared.
        user.is_staff = False
        user.is_superuser = False

    return user

def set_default_password(user, password):
    """Set user password with proper handling"""
    if password:
        user.set_password(password)
    else:
        user.set_password('defaultpassword123')
