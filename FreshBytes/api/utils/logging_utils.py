"""
Logging utilities for consistent logging across the FreshBytes API.
"""
import logging
import time
from functools import wraps
from django.utils import timezone

# Get logger for this module
logger = logging.getLogger(__name__)

def log_function_call(func_name=None):
    """
    Decorator to log function calls with timing information.
    
    Usage:
        @log_function_call()
        def my_function():
            pass
            
        @log_function_call("Custom Function Name")
        def another_function():
            pass
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            function_name = func_name or func.__name__
            start_time = time.time()
            
            logger.info(f"Function {function_name} called with args: {args}, kwargs: {kwargs}")
            
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                logger.info(f"Function {function_name} completed successfully in {execution_time:.3f}s")
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(f"Function {function_name} failed after {execution_time:.3f}s: {str(e)}")
                raise
        return wrapper
    return decorator

def log_api_request(view_name=None):
    """
    Decorator to log API request details.
    
    Usage:
        @log_api_request("Product List")
        def product_list(request):
            pass
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            view_name_final = view_name or view_func.__name__
            start_time = time.time()
            
            # Log request details
            logger.info(f"API Request: {request.method} {request.path} - View: {view_name_final}")
            logger.debug(f"Request Headers: {dict(request.headers)}")
            logger.debug(f"Request User: {request.user}")
            
            try:
                response = view_func(request, *args, **kwargs)
                execution_time = time.time() - start_time
                
                # Log response details
                logger.info(f"API Response: {response.status_code} - {view_name_final} - {execution_time:.3f}s")
                
                return response
            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(f"API Error: {view_name_final} - {str(e)} - {execution_time:.3f}s")
                raise
        return wrapper
    return decorator

def log_database_operation(operation_name=None):
    """
    Decorator to log database operations.
    
    Usage:
        @log_database_operation("Create User")
        def create_user(data):
            pass
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            operation_name_final = operation_name or func.__name__
            start_time = time.time()
            
            logger.info(f"Database Operation: {operation_name_final} started")
            
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                logger.info(f"Database Operation: {operation_name_final} completed in {execution_time:.3f}s")
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(f"Database Operation: {operation_name_final} failed after {execution_time:.3f}s: {str(e)}")
                raise
        return wrapper
    return decorator

def log_security_event(event_type, user_id=None, details=None, ip_address=None, user_agent=None):
    """
    Log security-related events.
    
    Args:
        event_type (str): Type of security event (LOGIN_SUCCESS, LOGIN_FAILED, LOGOUT_SUCCESS, etc.)
        user_id (str): User ID
        details (dict): Details about the event
        ip_address (str): IP address of the request
        user_agent (str): User agent string
    """
    security_logger = logging.getLogger('django.security')
    
    log_data = {
        'event_type': event_type,
        'user_id': user_id or 'anonymous',
        'timestamp': timezone.now().isoformat(),
        'ip_address': ip_address or 'unknown',
        'user_agent': user_agent or 'unknown',
        'details': details or {}
    }
    
    security_logger.warning(f"Security Event: {event_type} - User: {log_data['user_id']} - IP: {log_data['ip_address']} - Details: {log_data['details']}")

def log_performance_metric(metric_name, value, unit=None, tags=None):
    """
    Log performance metrics for monitoring.
    
    Args:
        metric_name (str): Name of the metric
        value (float): Metric value
        unit (str): Unit of measurement (ms, MB, etc.)
        tags (dict): Additional tags for the metric
    """
    unit_str = f" {unit}" if unit else ""
    tags_str = f" - Tags: {tags}" if tags else ""
    
    logger.info(f"Performance Metric: {metric_name} = {value}{unit_str}{tags_str}")

def log_business_event(event_type, user_id=None, admin_user_id=None, details=None):
    """
    Log business events for analytics and monitoring.
    
    Args:
        event_type (str): Type of business event (USER_ENABLED, USER_DISABLED, CHECKOUT_SUCCESS, etc.)
        user_id (str): User ID (target user for the event)
        admin_user_id (str): Admin user ID (if admin performed the action)
        details (dict): Additional event data
    """
    business_logger = logging.getLogger('api.business')
    
    log_data = {
        'event_type': event_type,
        'user_id': user_id or 'anonymous',
        'admin_user_id': admin_user_id,
        'timestamp': timezone.now().isoformat(),
        'details': details or {}
    }
    
    admin_info = f" - Admin: {admin_user_id}" if admin_user_id else ""
    business_logger.info(f"Business Event: {event_type} - User: {log_data['user_id']}{admin_info} - Details: {log_data['details']}")

# Convenience functions for common logging patterns
def log_user_activity(activity, user_id, details=None):
    """Log user activities for audit purposes."""
    log_business_event(
        event_type="user_activity",
        user_id=user_id,
        details={"activity": activity, "details": details or ""}
    )

def log_order_event(event_type, order_id, user_id, details=None):
    """Log order-related events."""
    log_business_event(
        event_type=f"order_{event_type}",
        user_id=user_id,
        details={"order_id": order_id, "details": details or ""}
    )

def log_product_event(event_type, product_id, user_id, details=None):
    """Log product-related events."""
    log_business_event(
        event_type=f"product_{event_type}",
        user_id=user_id,
        details={"product_id": product_id, "details": details or ""}
    ) 