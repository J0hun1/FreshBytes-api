"""
Permission classes for FreshBytes API.
Supports both Django Groups and legacy role field for backward compatibility.
"""

from rest_framework.permissions import BasePermission


class HasGroupPermission(BasePermission):
    """
    Base permission class that checks if user belongs to specific groups.
    Can be used as a base for other permission classes.
    """
    required_groups = []
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        return any(request.user.groups.filter(name=group).exists() 
                  for group in self.required_groups)


class IsAdminGroup(HasGroupPermission):
    """Permission that allows access only to users in Admin group"""
    required_groups = ['Admin']


class IsSellerGroup(HasGroupPermission):
    """Permission that allows access only to users in Seller group"""
    required_groups = ['Seller']


class IsCustomerGroup(HasGroupPermission):
    """Permission that allows access only to users in Customer group"""
    required_groups = ['Customer']


class IsSellerOrAdminGroup(HasGroupPermission):
    """Permission that allows access to users in Seller OR Admin groups"""
    required_groups = ['Seller', 'Admin']


class IsCustomerOrSellerGroup(HasGroupPermission):
    """Permission that allows access to users in Customer OR Seller groups"""
    required_groups = ['Customer', 'Seller']


# Backward compatibility classes that support both groups and role field
class IsAdmin(BasePermission):
    """
    Backward compatible permission class for admin users.
    Checks both Django groups and legacy role field.
    """
    def has_permission(self, request, view):
        return (request.user and request.user.is_authenticated and
                (request.user.groups.filter(name='Admin').exists() or 
                 request.user.role == 'admin'))


class IsSeller(BasePermission):
    """
    Backward compatible permission class for seller users.
    Checks both Django groups and legacy role field.
    """
    def has_permission(self, request, view):
        return (request.user and request.user.is_authenticated and
                (request.user.groups.filter(name='Seller').exists() or 
                 request.user.role == 'seller'))


class IsCustomer(BasePermission):
    """
    Backward compatible permission class for customer users.
    Checks both Django groups and legacy role field.
    """
    def has_permission(self, request, view):
        return (request.user and request.user.is_authenticated and
                (request.user.groups.filter(name='Customer').exists() or 
                 request.user.role == 'customer'))


class IsSellerOrAdmin(BasePermission):
    """
    Backward compatible permission class for seller or admin users.
    Checks both Django groups and legacy role field.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Check groups first, then fallback to role field
        is_admin = (request.user.groups.filter(name='Admin').exists() or 
                   request.user.role == 'admin')
        is_seller = (request.user.groups.filter(name='Seller').exists() or 
                    request.user.role == 'seller')
        
        return is_admin or is_seller


# Object-level permissions
class IsOwnerOrAdmin(BasePermission):
    """
    Permission that allows access to object owners or admin users.
    Requires the object to have a 'user' or 'user_id' attribute.
    """
    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Admin users can access everything
        if (request.user.groups.filter(name='Admin').exists() or 
            request.user.role == 'admin'):
            return True
        
        # Check if user owns the object
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'user_id'):
            return obj.user_id == request.user
        
        return False


class IsSellerOwnerOrAdmin(BasePermission):
    """
    Permission for seller-specific objects.
    Allows access to sellers who own the object or admin users.
    """
    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Admin users can access everything
        if (request.user.groups.filter(name='Admin').exists() or 
            request.user.role == 'admin'):
            return True
        
        # Check if user is a seller and owns the object
        is_seller = (request.user.groups.filter(name='Seller').exists() or 
                    request.user.role == 'seller')
        
        if not is_seller:
            return False
        
        # Check ownership through seller relationship
        if hasattr(obj, 'seller_id') and hasattr(obj.seller_id, 'user_id'):
            return obj.seller_id.user_id == request.user
        elif hasattr(obj, 'user_id'):
            return obj.user_id == request.user
        
        return False


# Custom permission decorators for function-based views
def require_roles(*roles):
    """
    Decorator for function-based views that require specific roles.
    Supports both Django groups and legacy role field.
    
    Usage:
        @require_roles('admin', 'seller')
        def my_view(request):
            # Only admins and sellers can access
            pass
    """
    from functools import wraps
    from django.http import JsonResponse
    
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return JsonResponse({'error': 'Authentication required'}, status=401)
            
            # Check if user has any of the required roles
            has_permission = False
            for role in roles:
                group_name = role.capitalize()
                if (request.user.groups.filter(name=group_name).exists() or 
                    request.user.role == role.lower()):
                    has_permission = True
                    break
            
            if not has_permission:
                return JsonResponse({
                    'error': f'Insufficient permissions. Required roles: {", ".join(roles)}'
                }, status=403)
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def require_group_permission(permission_codename):
    """
    Decorator that checks if user has a specific permission through groups.
    
    Usage:
        @require_group_permission('can_approve_products')
        def approve_product_view(request, product_id):
            # Only users with 'can_approve_products' permission can access
            pass
    """
    from functools import wraps
    from django.http import JsonResponse
    
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return JsonResponse({'error': 'Authentication required'}, status=401)
            
            if not request.user.has_perm(f'api.{permission_codename}'):
                return JsonResponse({
                    'error': f'Permission denied. Required permission: {permission_codename}'
                }, status=403)
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator 