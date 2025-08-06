# Testing the Verification System

This guide explains how to use the `test_verification.py` file to test the user verification system in the FreshBytes API.

## Overview

The verification system ensures that users must verify either their phone number or email address before they can:
- Add items to cart
- Create reviews  
- Make transactions/checkout

Users can always login and view products without verification.

## Running the Tests

### Prerequisites

1. Make sure you're in the Django project directory:
   ```bash
   cd FreshBytes
   ```

2. Ensure your database is set up and migrations are applied:
   ```bash
   python manage.py migrate
   ```

### Running All Verification Tests

```bash
python manage.py test api.tests.test_verification.VerificationTestCase -v 2
```

### Running Specific Tests

```bash
# Test verification utility functions
python manage.py test api.tests.test_verification.VerificationTestCase.test_verification_utility_functions -v 2

# Test verification status API endpoint
python manage.py test api.tests.test_verification.VerificationTestCase.test_verification_status_api -v 2

# Test verification status utility functions
python manage.py test api.tests.test_verification.VerificationTestCase.test_verification_status_utility_functions -v 2

# Test verification messages
python manage.py test api.tests.test_verification.VerificationTestCase.test_verification_messages -v 2
```

## Test Structure

The test file contains the following test methods:

### 1. `test_verification_utility_functions()`

Tests the core verification logic:
- **Unverified users**: Should fail verification checks
- **Phone verified users**: Should pass basic verification
- **Email verified users**: Should pass basic verification  
- **Fully verified users**: Should pass all verification levels
- **Partial verification with require_both=True**: Should fail

### 2. `test_verification_status_api()`

Tests the API endpoint `/api/auth/verification-status/`:
- Verifies the endpoint returns correct status codes
- Checks that unverified users get proper restrictions
- Ensures verified users get proper permissions

### 3. `test_verification_status_utility_functions()`

Tests the `get_verification_status()` utility function:
- Tests all verification status combinations
- Verifies boolean flags are correct
- Ensures status logic works properly

### 4. `test_verification_messages()`

Tests the `get_verification_message()` utility function:
- Verifies appropriate messages for each verification state
- Ensures messages are user-friendly and helpful

## Test Data Setup

The test creates 4 different user types:

1. **Unverified User**: No phone or email verified
2. **Phone Verified User**: Only phone number verified
3. **Email Verified User**: Only email address verified  
4. **Fully Verified User**: Both phone and email verified

## Expected Test Results

When tests pass, you should see output like:

```
test_verification_messages (api.tests.test_verification.VerificationTestCase.test_verification_messages)
Test verification message utility function ... ok
test_verification_status_api (api.tests.test_verification.VerificationTestCase.test_verification_status_api)
Test verification status API endpoint ... ok
test_verification_status_utility_functions (api.tests.test_verification.VerificationTestCase.test_verification_status_utility_functions)
Test verification status utility functions ... ok
test_verification_utility_functions (api.tests.test_verification.VerificationTestCase.test_verification_utility_functions)
Test verification utility functions ... ok

----------------------------------------------------------------------
Ran 4 tests in 5.651s

OK
```

## Manual Testing

You can also test the verification system manually:

### 1. Check Verification Status API

```bash
# Start the development server
python manage.py runserver

# Then make a GET request to:
GET /api/auth/verification-status/
Authorization: Bearer <your_jwt_token>
```

Expected response for unverified user:
```json
{
  "user_id": "uuid",
  "email": "user@example.com", 
  "verification_status": {
    "phone_verified": false,
    "email_verified": false,
    "fully_verified": false,
    "partially_verified": false,
    "verification_required": true,
    "missing_verifications": {
      "phone": true,
      "email": true
    }
  },
  "message": "Please verify either your phone number or email address to access all features.",
  "can_perform_actions": {
    "can_add_to_cart": false,
    "can_make_reviews": false,
    "can_make_transactions": false,
    "can_view_products": true,
    "can_login": true
  }
}
```

### 2. Test Protected Endpoints

Try accessing protected endpoints with unverified users:

```bash
# Cart endpoint (should return 403)
GET /api/carts/
Authorization: Bearer <unverified_user_token>

# Reviews endpoint (should return 403)
POST /api/reviews/
Authorization: Bearer <unverified_user_token>

# Order checkout (should return 403)
POST /api/orders/checkout/
Authorization: Bearer <unverified_user_token>
```

Expected error response:
```json
{
  "error": "Verification Required",
  "message": "You must verify either your phone number or email address before performing this action.",
  "code": "VERIFICATION_REQUIRED"
}
```

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Ensure your database is running
   - Check your database settings in `settings.py`
   - Run `python manage.py migrate` to apply migrations

2. **Import Errors**
   - Make sure you're in the correct directory (`FreshBytes/`)
   - Check that all required packages are installed
   - Verify the test file is in the correct location

3. **Test Failures**
   - Check that the verification system is properly implemented
   - Verify that permission classes are correctly applied
   - Ensure utility functions are working as expected

### Debugging Tests

To get more detailed output, run tests with higher verbosity:

```bash
python manage.py test api.tests.test_verification.VerificationTestCase -v 3
```

### Running Tests in Isolation

To run tests without affecting your main database:

```bash
# This creates a separate test database
python manage.py test api.tests.test_verification.VerificationTestCase --keepdb
```

## Extending the Tests

To add more test cases:

1. **Add new test methods** to the `VerificationTestCase` class
2. **Create additional user scenarios** in the `setUp()` method
3. **Test edge cases** like inactive users, deleted users, etc.
4. **Test integration** with other parts of the system

Example of adding a new test:

```python
def test_inactive_user_verification(self):
    """Test verification with inactive user"""
    self.user_phone_verified.is_active = False
    self.user_phone_verified.save()
    
    with self.assertRaises(Exception):
        check_user_verification(self.user_phone_verified, require_both=False)
```

## Continuous Integration

For CI/CD pipelines, you can run the tests with:

```bash
# Run all tests
python manage.py test

# Run only verification tests
python manage.py test api.tests.test_verification

# Run with coverage
coverage run --source='.' manage.py test api.tests.test_verification
coverage report
```

## Best Practices

1. **Always run tests** before deploying changes
2. **Test both positive and negative cases**
3. **Verify error messages** are user-friendly
4. **Test edge cases** and boundary conditions
5. **Keep tests focused** on specific functionality
6. **Use descriptive test names** that explain what's being tested

## Support

If you encounter issues with the tests:

1. Check the Django documentation on testing
2. Review the verification system implementation
3. Examine the test output for specific error messages
4. Verify that all dependencies are properly installed
5. Ensure the database schema matches the test expectations 