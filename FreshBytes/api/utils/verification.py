from django.core.exceptions import ValidationError

def check_user_verification(user, require_both=False):
    """
    Check if user has required verification status.
    
    Args:
        user: User instance
        require_both: If True, requires both phone and email verified.
                     If False, requires either phone or email verified.
    
    Returns:
        bool: True if user meets verification requirements
    
    Raises:
        ValidationError: If user doesn't meet verification requirements
    """
    if not user.is_authenticated:
        raise ValidationError("User must be authenticated.")
    
    if not user.is_active:
        raise ValidationError("Your account is inactive. Please contact support.")
    
    if user.is_deleted:
        raise ValidationError("Your account has been deleted. Please contact support.")
    
    if require_both:
        if not user.phone_verified or not user.email_verified:
            missing = []
            if not user.phone_verified:
                missing.append("phone number")
            if not user.email_verified:
                missing.append("email address")
            
            raise ValidationError(
                f"You must verify both your {' and '.join(missing)} before performing this action."
            )
    else:
        if not user.phone_verified and not user.email_verified:
            raise ValidationError(
                "You must verify either your phone number or email address before performing this action."
            )
    
    return True

def get_verification_status(user):
    """
    Get detailed verification status for a user.
    
    Args:
        user: User instance
    
    Returns:
        dict: Verification status information
    """
    return {
        'phone_verified': user.phone_verified,
        'email_verified': user.email_verified,
        'fully_verified': user.phone_verified and user.email_verified,
        'partially_verified': user.phone_verified or user.email_verified,
        'verification_required': not (user.phone_verified or user.email_verified),
        'missing_verifications': {
            'phone': not user.phone_verified,
            'email': not user.email_verified
        }
    }

def get_verification_message(user):
    """
    Get a user-friendly message about verification status.
    
    Args:
        user: User instance
    
    Returns:
        str: User-friendly verification message
    """
    if user.phone_verified and user.email_verified:
        return "Your account is fully verified."
    elif user.phone_verified:
        return "Your phone number is verified. Please verify your email address for full access."
    elif user.email_verified:
        return "Your email address is verified. Please verify your phone number for full access."
    else:
        return "Please verify either your phone number or email address to access all features." 