# User Verification System

## Overview

The FreshBytes API now includes a comprehensive user verification system that ensures users have verified their contact information before performing certain actions. Users can login and view products without verification, but must verify either their phone number or email address to perform transactions, add reviews, or add items to cart.

## Verification Requirements

### What Requires Verification
- **Adding items to cart** - Users must have either phone or email verified
- **Creating reviews** - Users must have either phone or email verified  
- **Making transactions/checkout** - Users must have either phone or email verified

### What Doesn't Require Verification
- **Login** - Users can always login
- **Viewing products** - Users can always browse and view products
- **Viewing categories** - Users can always browse categories
- **Basic account management** - Users can update their profile

## Implementation Details

### Permission Classes

#### `IsVerifiedUser`
- Requires users to have **either** phone or email verified
- Used for cart, reviews, and transactions
- Allows partial verification (one of the two)

#### `IsFullyVerifiedUser` 
- Requires users to have **both** phone and email verified
- For future use with sensitive operations
- Requires complete verification

### Utility Functions

#### `check_user_verification(user, require_both=False)`
- Validates user verification status
- `require_both=False`: Requires either phone or email verified
- `require_both=True`: Requires both phone and email verified
- Raises `ValidationError` if requirements not met

#### `get_verification_status(user)`
- Returns detailed verification status object
- Includes boolean flags for each verification type
- Provides helpful status information

#### `get_verification_message(user)`
- Returns user-friendly verification message
- Explains what needs to be verified
- Provides guidance for next steps

### API Endpoints

#### `GET /api/auth/verification-status/`
Returns user's verification status and what actions they can perform:

```json
{
  "user_id": "uuid",
  "email": "user@example.com",
  "verification_status": {
    "phone_verified": false,
    "email_verified": true,
    "fully_verified": false,
    "partially_verified": true,
    "verification_required": false,
    "missing_verifications": {
      "phone": true,
      "email": false
    }
  },
  "message": "Your email address is verified. Please verify your phone number for full access.",
  "can_perform_actions": {
    "can_add_to_cart": true,
    "can_make_reviews": true,
    "can_make_transactions": true,
    "can_view_products": true,
    "can_login": true
  }
}
```

## Error Handling

### Custom Exception Handler
The system includes a custom exception handler that provides clear error messages:

```json
{
  "error": "Verification Required",
  "message": "You must verify either your phone number or email address before performing this action.",
  "code": "VERIFICATION_REQUIRED"
}
```

### HTTP Status Codes
- `403 Forbidden`: When verification is required but not met
- `400 Bad Request`: For other validation errors
- `200 OK`: When verification requirements are satisfied

## Usage Examples

### Frontend Integration

#### Check Verification Status
```javascript
// Check if user can perform actions
const response = await fetch('/api/auth/verification-status/', {
  headers: { 'Authorization': `Bearer ${token}` }
});
const data = await response.json();

if (!data.can_perform_actions.can_add_to_cart) {
  showVerificationPrompt(data.message);
}
```

#### Handle Verification Errors
```javascript
try {
  const response = await fetch('/api/carts/', {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${token}` },
    body: JSON.stringify(cartData)
  });
  
  if (response.status === 403) {
    const error = await response.json();
    if (error.code === 'VERIFICATION_REQUIRED') {
      showVerificationModal(error.message);
    }
  }
} catch (error) {
  console.error('Cart operation failed:', error);
}
```

### Backend Usage

#### In Views
```python
from ..permissions import IsVerifiedUser

class CartViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, IsVerifiedUser]
    # ... rest of view
```

#### In Services
```python
from ..utils.verification import check_user_verification

def add_to_cart(user, product_id, quantity):
    # Validate user can use cart
    check_user_verification(user, require_both=False)
    # ... rest of function
```

## Testing

The system includes comprehensive tests in `api/tests/test_verification.py` that verify:

- Verification utility functions work correctly
- API endpoints return proper verification status
- Permission classes block unverified users
- Error messages are clear and helpful

Run tests with:
```bash
python manage.py test api.tests.test_verification
```

## Migration Notes

### For Existing Users
- Existing users will need to verify their contact information
- The system gracefully handles unverified users
- No data migration required

### For Frontend Applications
- Update API calls to handle 403 verification errors
- Add verification status checks before cart/review/transaction operations
- Implement verification prompts for better UX

## Future Enhancements

### Planned Features
- Email verification workflow
- SMS verification workflow  
- Admin verification management
- Verification expiration dates
- Re-verification requirements

### Configuration Options
- Configurable verification requirements per action
- Different verification levels (basic, enhanced, premium)
- Time-based verification requirements

## Security Considerations

- Verification status is checked on every protected action
- No bypass mechanisms for unverified users
- Clear audit trail of verification status changes
- Secure verification token generation and validation

## Support

For questions about the verification system:
1. Check the test files for usage examples
2. Review the permission classes in `api/permissions.py`
3. Examine the utility functions in `api/utils/verification.py`
4. Test with the verification status endpoint 