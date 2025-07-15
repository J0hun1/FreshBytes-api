#!/usr/bin/env python
"""
Script to assign existing users to appropriate Django groups based on their role field.
Run this after setting up groups with: python manage.py setup_groups
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FreshBytes.settings')
django.setup()

from django.contrib.auth.models import Group
from api.models import User

def assign_users_to_groups():
    """Assign existing users to appropriate groups based on their role field"""
    
    # Get or create groups
    try:
        admin_group = Group.objects.get(name='Admin')
        seller_group = Group.objects.get(name='Seller')
        customer_group = Group.objects.get(name='Customer')
    except Group.DoesNotExist:
        print("Error: Groups not found. Please run 'python manage.py setup_groups' first.")
        return False
    
    # Statistics tracking
    assigned_counts = {'admin': 0, 'seller': 0, 'customer': 0, 'unknown': 0}
    
    print("Starting user group assignment...")
    print(f"Total users in database: {User.objects.count()}")
    
    # Assign existing users to appropriate groups
    for user in User.objects.all():
        print(f"Processing user: {user.user_email} (role: {user.role})")
        
        # Clear existing group memberships first
        user.groups.clear()
        
        if user.role == 'admin':
            user.groups.add(admin_group)
            assigned_counts['admin'] += 1
            print(f"  → Assigned to Admin group")
        elif user.role == 'seller':
            user.groups.add(seller_group)
            assigned_counts['seller'] += 1
            print(f"  → Assigned to Seller group")
        elif user.role == 'customer':
            user.groups.add(customer_group)
            assigned_counts['customer'] += 1
            print(f"  → Assigned to Customer group")
        else:
            # Default unknown roles to customer
            user.groups.add(customer_group)
            assigned_counts['unknown'] += 1
            print(f"  → Unknown role '{user.role}', assigned to Customer group")
    
    print("\n" + "="*50)
    print("USER GROUP ASSIGNMENT COMPLETED")
    print("="*50)
    print(f"Admin group: {assigned_counts['admin']} users")
    print(f"Seller group: {assigned_counts['seller']} users")
    print(f"Customer group: {assigned_counts['customer']} users")
    print(f"Unknown roles (assigned to Customer): {assigned_counts['unknown']} users")
    print("="*50)
    
    return True

def verify_assignments():
    """Verify that the group assignments are correct"""
    print("\nVerifying group assignments...")
    
    admin_group = Group.objects.get(name='Admin')
    seller_group = Group.objects.get(name='Seller')
    customer_group = Group.objects.get(name='Customer')
    
    print(f"\nAdmin group has {admin_group.user_set.count()} users:")
    for user in admin_group.user_set.all():
        print(f"  - {user.user_email} (role: {user.role})")
    
    print(f"\nSeller group has {seller_group.user_set.count()} users:")
    for user in seller_group.user_set.all():
        print(f"  - {user.user_email} (role: {user.role})")
    
    print(f"\nCustomer group has {customer_group.user_set.count()} users:")
    for user in customer_group.user_set.all():
        print(f"  - {user.user_email} (role: {user.role})")

if __name__ == "__main__":
    success = assign_users_to_groups()
    if success:
        verify_assignments()
        print("\n✅ User group assignment completed successfully!")
        print("\nNext steps:")
        print("1. Add helper methods to User model")
        print("2. Create new permission classes")
        print("3. Test the new permission system")
    else:
        print("❌ Assignment failed. Please check the error messages above.") 