from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from api.models import Product, Seller, Promo, Reviews, Order, Cart, CartItem

class Command(BaseCommand):
    help = 'Setup user groups and permissions for role-based access control'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Reset all groups and permissions before creating new ones',
        )
    
    def handle(self, *args, **options):
        if options['reset']:
            self.stdout.write(self.style.WARNING('Resetting all groups and permissions...'))
            Group.objects.filter(name__in=['Admin', 'Seller', 'Customer']).delete()
        
        # Create groups
        admin_group, created = Group.objects.get_or_create(name='Admin')
        if created:
            self.stdout.write(self.style.SUCCESS('Created Admin group'))
        else:
            self.stdout.write('Admin group already exists')
            
        seller_group, created = Group.objects.get_or_create(name='Seller')
        if created:
            self.stdout.write(self.style.SUCCESS('Created Seller group'))
        else:
            self.stdout.write('Seller group already exists')
            
        customer_group, created = Group.objects.get_or_create(name='Customer')
        if created:
            self.stdout.write(self.style.SUCCESS('Created Customer group'))
        else:
            self.stdout.write('Customer group already exists')
        
        # Get content types for our models
        content_types = {
            'product': ContentType.objects.get_for_model(Product),
            'seller': ContentType.objects.get_for_model(Seller),
            'promo': ContentType.objects.get_for_model(Promo),
            'reviews': ContentType.objects.get_for_model(Reviews),
            'order': ContentType.objects.get_for_model(Order),
            'cart': ContentType.objects.get_for_model(Cart),
            'cartitem': ContentType.objects.get_for_model(CartItem),
        }
        
        # Create custom permissions
        custom_permissions = [
            ('can_approve_products', 'Can approve products', content_types['product']),
            ('can_feature_products', 'Can feature products', content_types['product']),
            ('can_bulk_edit_products', 'Can bulk edit products', content_types['product']),
            ('can_view_all_orders', 'Can view all orders', content_types['order']),
            ('can_manage_sellers', 'Can manage sellers', content_types['seller']),
            ('can_view_seller_stats', 'Can view seller statistics', content_types['seller']),
            ('can_moderate_reviews', 'Can moderate reviews', content_types['reviews']),
        ]
        
        created_permissions = []
        for codename, name, content_type in custom_permissions:
            permission, created = Permission.objects.get_or_create(
                codename=codename,
                name=name,
                content_type=content_type
            )
            if created:
                created_permissions.append(permission)
                self.stdout.write(f'Created permission: {name}')
        
        if created_permissions:
            self.stdout.write(self.style.SUCCESS(f'Created {len(created_permissions)} custom permissions'))
        else:
            self.stdout.write('All custom permissions already exist')
        
        # Assign permissions to groups
        self._setup_admin_permissions(admin_group)
        self._setup_seller_permissions(seller_group)
        self._setup_customer_permissions(customer_group)
        
        self.stdout.write(
            self.style.SUCCESS('Successfully setup groups and permissions!')
        )
        
        # Display summary
        self._display_summary()
    
    def _setup_admin_permissions(self, group):
        """Admins get all permissions"""
        permissions = Permission.objects.all()
        group.permissions.set(permissions)
        self.stdout.write(f'Assigned {permissions.count()} permissions to Admin group')
    
    def _setup_seller_permissions(self, group):
        """Sellers can manage their own products, promos, and view orders"""
        permission_codes = [
            # Product permissions
            'add_product', 'change_product', 'delete_product', 'view_product',
            'can_bulk_edit_products',
            
            # Promo permissions
            'add_promo', 'change_promo', 'delete_promo', 'view_promo',
            
            # Order permissions (view only for their products)
            'view_order',
            
            # Review permissions (view and respond)
            'view_reviews', 'change_reviews',
            
            # Seller profile permissions
            'change_seller', 'view_seller', 'can_view_seller_stats',
            
            # Cart permissions (for managing their own cart)
            'view_cart', 'add_cart', 'change_cart',
            'view_cartitem', 'add_cartitem', 'change_cartitem', 'delete_cartitem',
        ]
        
        permissions = Permission.objects.filter(codename__in=permission_codes)
        group.permissions.set(permissions)
        self.stdout.write(f'Assigned {permissions.count()} permissions to Seller group')
    
    def _setup_customer_permissions(self, group):
        """Customers can create reviews, manage cart, place orders"""
        permission_codes = [
            # Review permissions
            'add_reviews', 'change_reviews', 'delete_reviews', 'view_reviews',
            
            # Cart permissions
            'add_cart', 'change_cart', 'view_cart',
            'add_cartitem', 'change_cartitem', 'delete_cartitem', 'view_cartitem',
            
            # Order permissions
            'add_order', 'view_order',
            
            # View permissions for browsing
            'view_product', 'view_category', 'view_subcategory', 'view_seller',
        ]
        
        permissions = Permission.objects.filter(codename__in=permission_codes)
        group.permissions.set(permissions)
        self.stdout.write(f'Assigned {permissions.count()} permissions to Customer group')
    
    def _display_summary(self):
        """Display a summary of created groups and their permissions"""
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('GROUPS AND PERMISSIONS SUMMARY'))
        self.stdout.write('='*50)
        
        for group_name in ['Admin', 'Seller', 'Customer']:
            try:
                group = Group.objects.get(name=group_name)
                permission_count = group.permissions.count()
                self.stdout.write(f'\n{group_name} Group:')
                self.stdout.write(f'  - {permission_count} permissions assigned')
                self.stdout.write(f'  - {group.user_set.count()} users in this group')
            except Group.DoesNotExist:
                self.stdout.write(f'\n{group_name} Group: NOT FOUND')
        
        self.stdout.write('\n' + '='*50)
        self.stdout.write('Next steps:')
        self.stdout.write('1. Run migration to assign existing users to groups')
        self.stdout.write('2. Update permission classes in views.py')
        self.stdout.write('3. Test the new permission system')
        self.stdout.write('='*50) 