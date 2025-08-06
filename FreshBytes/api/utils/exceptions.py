from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError

def custom_exception_handler(exc, context):
    """
    Custom exception handler to provide better error messages
    for verification requirements and other business logic errors.
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)
    
    if response is not None:
        # Handle validation errors with custom messages
        if isinstance(exc, ValidationError):
            if "verify" in str(exc).lower():
                response.data = {
                    'error': 'Verification Required',
                    'message': str(exc),
                    'code': 'VERIFICATION_REQUIRED'
                }
                response.status_code = status.HTTP_403_FORBIDDEN
            else:
                response.data = {
                    'error': 'Validation Error',
                    'message': str(exc),
                    'code': 'VALIDATION_ERROR'
                }
        
        # Handle ValueError (from business logic)
        elif isinstance(exc, ValueError):
            if "verify" in str(exc).lower():
                response.data = {
                    'error': 'Verification Required',
                    'message': str(exc),
                    'code': 'VERIFICATION_REQUIRED'
                }
                response.status_code = status.HTTP_403_FORBIDDEN
            else:
                response.data = {
                    'error': 'Business Logic Error',
                    'message': str(exc),
                    'code': 'BUSINESS_LOGIC_ERROR'
                }
                response.status_code = status.HTTP_400_BAD_REQUEST
    
    return response 