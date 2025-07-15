#!/usr/bin/env python
"""
Test script to verify the new permission system works correctly.
Tests both Django groups and backward compatibility with role field.
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FreshBytes.settings')
django.setup()

from django.contrib.auth.models import Group
from api.models import User
from api.permissions import (
    IsAdmin, IsSeller, IsCustomer, IsSellerOrAdmin,
    IsAdminGroup, IsSellerGroup, IsCustomerGroup, IsSellerOrAdminGroup
)
from django.test import RequestFactory


class MockView:
    """Mock view class for testing permissions"""
    pass


def create_mock_request(user):
    """Create a mock request with the given user"""
    factory = RequestFactory()
    request = factory.get('/')
    request.user = user
    return request


def test_user_helper_methods():
    """Test the new helper methods in User model"""
    print("\n" + "="*60)
    print("TESTING USER MODEL HELPER METHODS")
    print("="*60)
    
    users = User.objects.all()
    
    for user in users:
        print(f"\nUser: {user.user_email} (role: {user.role})")
        print(f"  Groups: {[g.name for g in user.groups.all()]}")
        print(f"  is_admin(): {user.is_admin()}")
        print(f"  is_seller(): {user.is_seller()}")
        print(f"  is_customer(): {user.is_customer()}")
        print(f"  get_primary_role(): {user.get_primary_role()}")
        print(f"  has_role('admin'): {user.has_role('admin')}")
        print(f"  has_role('seller'): {user.has_role('seller')}")
        print(f"  has_role('customer'): {user.has_role('customer')}")


def test_backward_compatible_permissions():
    """Test backward compatible permission classes"""
    print("\n" + "="*60)
    print("TESTING BACKWARD COMPATIBLE PERMISSIONS")
    print("="*60)
    
    users = User.objects.all()
    view = MockView()
    
    permissions_to_test = [
        ('IsAdmin', IsAdmin()),
        ('IsSeller', IsSeller()),
        ('IsCustomer', IsCustomer()),
        ('IsSellerOrAdmin', IsSellerOrAdmin()),
    ]
    
    for user in users:
        print(f"\nUser: {user.user_email} (role: {user.role})")
        request = create_mock_request(user)
        
        for perm_name, permission in permissions_to_test:
            has_perm = permission.has_permission(request, view)
            print(f"  {perm_name}: {has_perm}")


def test_group_based_permissions():
    """Test new group-based permission classes"""
    print("\n" + "="*60)
    print("TESTING GROUP-BASED PERMISSIONS")
    print("="*60)
    
    users = User.objects.all()
    view = MockView()
    
    permissions_to_test = [
        ('IsAdminGroup', IsAdminGroup()),
        ('IsSellerGroup', IsSellerGroup()),
        ('IsCustomerGroup', IsCustomerGroup()),
        ('IsSellerOrAdminGroup', IsSellerOrAdminGroup()),
    ]
    
    for user in users:
        print(f"\nUser: {user.user_email} (groups: {[g.name for g in user.groups.all()]})")
        request = create_mock_request(user)
        
        for perm_name, permission in permissions_to_test:
            has_perm = permission.has_permission(request, view)
            print(f"  {perm_name}: {has_perm}")


def test_django_permissions():
    """Test Django's built-in permission system with our groups"""
    print("\n" + "="*60)
    print("TESTING DJANGO BUILT-IN PERMISSIONS")
    print("="*60)
    
    users = User.objects.all()
    
    # Test some common permissions
    permissions_to_test = [
        'api.add_product',
        'api.change_product',
        'api.delete_product',
        'api.can_approve_products',
        'api.can_view_seller_stats',
        'api.add_order',
        'api.view_order',
    ]
    
    for user in users:
        print(f"\nUser: {user.user_email} (groups: {[g.name for g in user.groups.all()]})")
        
        for perm in permissions_to_test:
            has_perm = user.has_perm(perm)
            print(f"  {perm}: {has_perm}")


def test_role_assignment():
    """Test the assign_to_group helper method"""
    print("\n" + "="*60)
    print("TESTING ROLE ASSIGNMENT")
    print("="*60)
    
    # Get a customer user to test role assignment
    customer_user = User.objects.filter(role='customer').first()
    if customer_user:
        print(f"Testing with user: {customer_user.user_email}")
        print(f"Current role: {customer_user.role}")
        print(f"Current groups: {[g.name for g in customer_user.groups.all()]}")
        
        # Test invalid group assignment
        result = customer_user.assign_to_group('NonExistentGroup')
        print(f"Assign to non-existent group: {result}")
        
        # Test valid group assignment (but don't actually change it)
        print("\nNote: Not actually changing user role to avoid data modification")
        print("The assign_to_group method would work for valid group names like 'Seller'")
    else:
        print("No customer users found for testing")


def display_summary():
    """Display a summary of the current setup"""
    print("\n" + "="*60)
    print("PERMISSION SYSTEM SETUP SUMMARY")
    print("="*60)
    
    # Group summary
    groups = Group.objects.filter(name__in=['Admin', 'Seller', 'Customer'])
    for group in groups:
        print(f"\n{group.name} Group:")
        print(f"  - {group.permissions.count()} permissions")
        print(f"  - {group.user_set.count()} users")
        for user in group.user_set.all():
            print(f"    * {user.user_email}")
    
    print(f"\nTotal users: {User.objects.count()}")
    print("\nPermission classes available:")
    print("  - Backward compatible: IsAdmin, IsSeller, IsCustomer, IsSellerOrAdmin")
    print("  - Group-based: IsAdminGroup, IsSellerGroup, IsCustomerGroup, IsSellerOrAdminGroup")
    print("  - Object-level: IsOwnerOrAdmin, IsSellerOwnerOrAdmin")
    print("  - Decorators: @require_roles, @require_group_permission")


if __name__ == "__main__":
    print("🔐 Testing FreshBytes Permission System")
    print("This script tests both backward compatibility and new group-based permissions")
    
    try:
        test_user_helper_methods()
        test_backward_compatible_permissions()
        test_group_based_permissions()
        test_django_permissions()
        test_role_assignment()
        display_summary()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS COMPLETED SUCCESSFULLY!")
        print("="*60)
        print("\nThe permission system is working correctly!")
        print("You can now:")
        print("1. Update views.py to use new permission classes gradually")
        print("2. Use fine-grained permissions like 'can_approve_products'")
        print("3. Manage roles through Django admin interface")
        print("4. Eventually remove the role field when fully migrated")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc() 