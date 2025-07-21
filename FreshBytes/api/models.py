from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.utils import timezone
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.contrib.auth.hashers import make_password
from django.core.validators import MinValueValidator, MaxValueValidator
from .services.product_services import update_seller_total_products
from .services.promo_services import update_products_has_promo_on_promo_save, update_products_has_promo_on_promo_delete, update_products_has_promo_on_m2m_change
from django.db.models.signals import pre_delete
from .choices import ProductStatus, Discount_Type, OrderStatus
import uuid
from django.conf import settings

class UserManager(BaseUserManager):
    def create_user(self, user_email, password=None, **extra_fields):
        """Create and save a user with a valid password.

        Security fix: a password **must** be provided. Removes the default
        plaintext password that previously existed.
        """
        if not user_email:
            raise ValueError('The Email field must be set')
        if not password:
            raise ValueError('Password must be provided')

        user_email = self.normalize_email(user_email)
        user = self.model(user_email=user_email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, user_email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(user_email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('seller', 'Seller'),
        ('customer', 'Customer'),
    ]

    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    user_name = models.CharField(max_length=255)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    user_email = models.EmailField(unique=True, null=True)
    password = models.CharField(max_length=128, null=True)
    user_phone = models.CharField(max_length=255)
    user_address = models.CharField(max_length=255)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'user_email'
    REQUIRED_FIELDS = ['user_name', 'first_name', 'last_name']

    def save(self, *args, **kwargs):
        from .services.users_services import validate_user_role
        
        # Ensure user_id is set (UUID will be generated automatically)
        self = validate_user_role(self)
        super().save(*args, **kwargs)
    
    # Group-based role checking methods (for new permission system)
    def is_admin(self):
        """Check if user is in Admin group or has admin role"""
        return self.groups.filter(name='Admin').exists() or self.role == 'admin'
    
    def is_seller(self):
        """Check if user is in Seller group or has seller role"""
        return self.groups.filter(name='Seller').exists() or self.role == 'seller'
    
    def is_customer(self):
        """Check if user is in Customer group or has customer role"""
        return self.groups.filter(name='Customer').exists() or self.role == 'customer'
    
    def has_role(self, role_name):
        """Check if user has a specific role (supports both groups and role field)"""
        group_name = role_name.capitalize()
        return (self.groups.filter(name=group_name).exists() or 
                self.role == role_name.lower())
    
    def get_primary_role(self):
        """Get the user's primary role based on group membership (falls back to role field)"""
        if self.groups.filter(name='Admin').exists():
            return 'admin'
        elif self.groups.filter(name='Seller').exists():
            return 'seller'
        elif self.groups.filter(name='Customer').exists():
            return 'customer'
        else:
            # Fallback to role field if no groups assigned
            return self.role
    
    def sync_role_with_groups(self):
        """Sync the role field with group membership (for backward compatibility)"""
        primary_role = self.get_primary_role()
        if self.role != primary_role:
            self.role = primary_role
            self.save(update_fields=['role'])
    
    def assign_to_group(self, group_name):
        """Helper method to assign user to a specific group"""
        from django.contrib.auth.models import Group
        try:
            group = Group.objects.get(name=group_name)
            self.groups.add(group)
            # Update role field to match
            self.role = group_name.lower()
            self.save(update_fields=['role'])
            return True
        except Group.DoesNotExist:
            return False

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        db_table = 'Users'

#SELLER
class Seller(models.Model):
    seller_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    user_id = models.OneToOneField(User, on_delete=models.CASCADE, related_name='seller_profile', db_column='user_id', null=True, blank=True)
    business_name = models.CharField(default="", max_length=255)
    business_email = models.EmailField(blank=True)
    business_phone = models.IntegerField(default="")
    business_address = models.CharField(default="", max_length=255, null=True)
    total_earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)
    total_products = models.IntegerField(default=0)
    total_orders = models.IntegerField(default=0)
    total_reviews = models.IntegerField(default=0)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    total_followers = models.IntegerField(default=0)
    total_likes = models.IntegerField(default=0)
    total_products_sold = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)

    def clean(self):
        from .services.seller_services import validate_seller
        validate_seller(self)
        
    def save(self, *args, **kwargs):
        from .services.seller_services import initialize_seller_stats
        
        initialize_seller_stats(self)
        self.clean()
        
        if not self.business_email and self.user_id and self.user_id.user_email:
            self.business_email = self.user_id.user_email
            
        super().save(*args, **kwargs)

    def get_customers(self):
        """
        Returns a queryset of unique customers who have bought from this seller.
        """
        from .models import OrderItem
        customer_ids = OrderItem.objects.filter(
            product_id__seller_id=self,
            order_id__order_status='DELIVERED'
        ).values_list('order_id__user_id', flat=True).distinct()
        return User.objects.filter(user_id__in=customer_ids)

    def get_transactions(self):
        """
        Returns a queryset of all orders (transactions) involving this seller.
        """
        from .models import OrderItem, Order
        order_ids = OrderItem.objects.filter(
            product_id__seller_id=self
        ).values_list('order_id', flat=True).distinct()
        return Order.objects.filter(order_id__in=order_ids)

    def get_products_bought_by_customer(self, customer):
        """
        Returns a queryset of products bought by a specific customer from this seller.
        """
        from .models import OrderItem, Product
        product_ids = OrderItem.objects.filter(
            product_id__seller_id=self,
            order_id__user_id=customer,
            order_id__order_status='DELIVERED'
        ).values_list('product_id', flat=True).distinct()
        return Product.objects.filter(product_id__in=product_ids)
    

    class Meta:
        db_table = 'Seller'

#CATEGORY
class Category(models.Model):
    category_id = models.AutoField(primary_key=True)
    category_name = models.CharField(max_length=255, unique=True)
    category_description = models.CharField(max_length=255, default="")
    category_isActive = models.BooleanField(default=True)
    category_image = models.ImageField(upload_to='category_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Categories'

#SUBCATEGORY
class SubCategory(models.Model):
    sub_category_id = models.CharField(primary_key=True, max_length=10, unique=True, editable=False)
    category_id = models.ForeignKey(Category, on_delete=models.CASCADE, null=True)
    sub_category_name = models.CharField(max_length=255, default="", unique=True)
    sub_category_description = models.CharField(max_length=255)
    sub_category_image = models.ImageField(upload_to='sub_category_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        from .services.category_services import generate_subcategory_id, get_starting_counter
        
        if not self.sub_category_id:
            category_prefix = str(self.category_id.category_id) if self.category_id else "0"
            last_sub_category = SubCategory.objects.filter(
                category_id=self.category_id
            ).order_by('-created_at').first()
            
            starting_counter = get_starting_counter(category_prefix, last_sub_category)
            self.sub_category_id = generate_subcategory_id(category_prefix, starting_counter)
            
        super().save(*args, **kwargs)
    
#PRODUCT 
class Product(models.Model):
    product_id = models.CharField(primary_key=True, max_length=36, unique=True, editable=False, default=uuid.uuid4)
    seller_id = models.ForeignKey(Seller, on_delete=models.CASCADE, null=True)
    product_name = models.CharField(max_length=255)
    product_price = models.DecimalField(max_digits=10, decimal_places=2, default=0,
                                        validators=[MinValueValidator(0.01)])
    product_brief_description = models.CharField(max_length=255)
    product_full_description = models.CharField(max_length=255)
    product_discountedPrice = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    product_sku = models.CharField(max_length=50, null=True, blank=True)
    product_status = models.CharField(
        max_length=20,
        choices=[
            ('ROTTEN', 'Rotten'),
            ('SLIGHTLY_WITHERED', 'Slightly Withered'),
            ('FRESH', 'Fresh')
        ],
        default='FRESH'
    )
    product_location = models.CharField(max_length=255, null=True)
    sub_category_id = models.ForeignKey(SubCategory, on_delete=models.CASCADE, null=True)
    has_promo = models.BooleanField(default=False)
    weight = models.DecimalField(max_digits=10, decimal_places=2, default=0,
                                 validators=[MinValueValidator(0.01)])
    quantity = models.IntegerField(default=1, validators=[MinValueValidator(0)])
    post_date = models.DateTimeField(default=timezone.now)
    harvest_date = models.DateTimeField(null=True)
    is_active = models.BooleanField(default=True)
    review_count = models.IntegerField(default=0)
    top_rated = models.BooleanField(default=False)
    is_srp = models.BooleanField(default=False)
    is_discounted = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    sell_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    _skip_update = False  # Flag to prevent recursive updates

    @property
    def user_id(self):
        return self.seller_id.user_id.user_id if self.seller_id and self.seller_id.user_id else None

    @property
    def category_id(self):
        return self.sub_category_id.category_id if self.sub_category_id else None

    @property
    def discounted_amount(self):
        if self.product_discountedPrice is not None:
            return self.product_price - self.product_discountedPrice
        return None

    def update_discounted_price(self):
        if not self._skip_update and self.pk:  # Only update if product exists and not in recursive update
            from .services.product_services import update_product_discounted_price
            self._skip_update = True  # Set flag to prevent recursion
            try:
                update_product_discounted_price(self)
            finally:
                self._skip_update = False  # Reset flag

    def save(self, *args, **kwargs):
        from .services.product_services import generate_product_sku
        
        is_new = not self.pk  # Check if this is a new product
        
        # product_id auto-set by default using UUID

        if not self.product_sku:
            # Optionally auto-generate SKU (not enforced unique globally)
            try:
                self.product_sku = generate_product_sku(self)
            except Exception:
                pass  # leave blank if generator fails

        if self.product_price > 0 and (self.product_discountedPrice is None or self.product_discountedPrice <= 0):
            self.is_srp = True

        # First save the product
        super().save(*args, **kwargs)
        
        # Then update discount fields if it's not a new product and we're not in a recursive update
        if not is_new and not self._skip_update and 'update_fields' not in kwargs:
            self.update_discounted_price()

    def delete(self, using=None, keep_parents=False):
        self.is_deleted = True
        self.save()

    class Meta:
        db_table = 'Products'

class ProductManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)

class Product(models.Model):
    product_id = models.CharField(primary_key=True, max_length=36, unique=True, editable=False, default=uuid.uuid4)
    seller_id = models.ForeignKey(Seller, on_delete=models.CASCADE, null=True)
    product_name = models.CharField(max_length=255)
    product_price = models.DecimalField(max_digits=10, decimal_places=2, default=0,
                                        validators=[MinValueValidator(0.01)])
    product_brief_description = models.CharField(max_length=255)
    product_full_description = models.CharField(max_length=255)
    product_discountedPrice = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    product_sku = models.CharField(max_length=50, null=True, blank=True)
    product_status = models.CharField(
        max_length=20,
        choices=[
            ('ROTTEN', 'Rotten'),
            ('SLIGHTLY_WITHERED', 'Slightly Withered'),
            ('FRESH', 'Fresh')
        ],
        default='FRESH'
    )
    product_location = models.CharField(max_length=255, null=True)
    sub_category_id = models.ForeignKey(SubCategory, on_delete=models.CASCADE, null=True)
    has_promo = models.BooleanField(default=False)
    weight = models.DecimalField(max_digits=10, decimal_places=2, default=0,
                                 validators=[MinValueValidator(0.01)])
    quantity = models.IntegerField(default=1, validators=[MinValueValidator(0)])
    post_date = models.DateTimeField(default=timezone.now)
    harvest_date = models.DateTimeField(null=True)
    is_active = models.BooleanField(default=True)
    review_count = models.IntegerField(default=0)
    top_rated = models.BooleanField(default=False)
    is_srp = models.BooleanField(default=False)
    is_discounted = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    sell_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    _skip_update = False  # Flag to prevent recursive updates

    objects = ProductManager()  # Default manager excludes deleted
    all_objects = models.Manager()  # Includes deleted

    @property
    def user_id(self):
        return self.seller_id.user_id.user_id if self.seller_id and self.seller_id.user_id else None

    @property
    def category_id(self):
        return self.sub_category_id.category_id if self.sub_category_id else None

    @property
    def discounted_amount(self):
        if self.product_discountedPrice is not None:
            return self.product_price - self.product_discountedPrice
        return None

    def update_discounted_price(self):
        if not self._skip_update and self.pk:  # Only update if product exists and not in recursive update
            from .services.product_services import update_product_discounted_price
            self._skip_update = True  # Set flag to prevent recursion
            try:
                update_product_discounted_price(self)
            finally:
                self._skip_update = False  # Reset flag

    def save(self, *args, **kwargs):
        from .services.product_services import generate_product_sku
        
        is_new = not self.pk  # Check if this is a new product
        
        # product_id auto-set by default using UUID

        if not self.product_sku:
            # Optionally auto-generate SKU (not enforced unique globally)
            try:
                self.product_sku = generate_product_sku(self)
            except Exception:
                pass  # leave blank if generator fails

        if self.product_price > 0 and (self.product_discountedPrice is None or self.product_discountedPrice <= 0):
            self.is_srp = True

        # First save the product
        super().save(*args, **kwargs)
        
        # Then update discount fields if it's not a new product and we're not in a recursive update
        if not is_new and not self._skip_update and 'update_fields' not in kwargs:
            self.update_discounted_price()

    def delete(self, using=None, keep_parents=False):
        self.is_deleted = True
        self.save()

    class Meta:
        db_table = 'Products'

@receiver(post_save, sender=Product)
def update_seller_product_count_on_save(sender, instance, **kwargs):
    """Update the seller's product count when a product is saved."""
    if instance.seller_id:
        update_seller_total_products(instance.seller_id)


@receiver(post_delete, sender=Product)
def update_seller_product_count_on_delete(sender, instance, **kwargs):
    """Update the seller's product count when a product is deleted."""
    if instance.seller_id:
        update_seller_total_products(instance.seller_id)
            

#REVIEWS
class Reviews(models.Model):
    review_id = models.CharField(primary_key=True, max_length=10, unique=True, editable=False)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True, db_column='user_id')
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    review_rating = models.IntegerField(default=0,
                                       validators=[MinValueValidator(1), MaxValueValidator(5)])
    review_comment = models.CharField(max_length=255)
    review_date = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        from .services.review_services import generate_review_id, update_product_review_stats, update_seller_review_stats
        
        if not self.review_id:
            last_review = Reviews.objects.order_by('-created_at').first()
            self.review_id = generate_review_id(last_review)
            
        super().save(*args, **kwargs)
        
        # Update related statistics
        if self.product_id:
            update_product_review_stats(self.product_id)
            if self.product_id.seller_id:
                update_seller_review_stats(self.product_id.seller_id)
    
    class Meta:
        db_table = 'Reviews'


#PROMO
class PromoProduct(models.Model):
    """Intermediate model for Promo-Product relationship"""
    promo = models.ForeignKey('Promo', on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update product's discount fields
        self.product.update_discounted_price()

    def delete(self, *args, **kwargs):
        product = self.product  # Store reference before deletion
        super().delete(*args, **kwargs)
        # Update product's discount fields after removing promo
        product.update_discounted_price()

    class Meta:
        db_table = 'PromoProduct'
        unique_together = ('promo', 'product')

class Promo(models.Model):
    # Surrogate UUID primary key for promos (seller-agnostic, best-practice)
    promo_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    seller_id = models.ForeignKey(Seller, on_delete=models.CASCADE, default=None)
    product_id = models.ManyToManyField(Product, through='PromoProduct', related_name='promos')
    promo_description = models.CharField(max_length=255, default="")
    promo_name = models.CharField(max_length=255)
    discount_type = models.CharField(
        max_length=255,
        choices=[
            ('PERCENTAGE', 'Percentage'),
            ('FIXED', 'Fixed')
        ],
        default='FIXED'
    )
    discount_amount = models.IntegerField(default=0)
    discount_percentage = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    promo_start_date = models.DateTimeField(default=timezone.now)
    promo_end_date = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        """Custom save to ensure valid date range and propagate promo flags."""
        from .services.promo_services import update_products_has_promo_on_promo_save

        # Ensure end date is after start date
        if self.promo_end_date <= self.promo_start_date:
            self.promo_end_date = self.promo_start_date + timezone.timedelta(days=7)

        # Save normally (UUID is generated automatically)
        super().save(*args, **kwargs)

        # Update associated products
        update_products_has_promo_on_promo_save(self)

    class Meta:
        db_table = 'Promo'


# Signal handlers for Promo-Product relationship
@receiver(post_save, sender=Promo)
def handle_promo_save(sender, instance, created, **kwargs):
    """Handle promo creation and updates"""
    from .services.promo_services import update_products_has_promo_on_promo_save
    if not kwargs.get('raw', False):
        update_products_has_promo_on_promo_save(instance)

@receiver(pre_delete, sender=Promo)
def handle_promo_pre_delete(sender, instance, **kwargs):
    """Handle promo deletion by updating products before the promo is deleted"""
    from .services.promo_services import update_products_has_promo_on_promo_delete
    update_products_has_promo_on_promo_delete(instance)

@receiver(models.signals.m2m_changed, sender=Promo.product_id.through)
def handle_promo_m2m_changes(sender, instance, action, pk_set, **kwargs):
    """Handle changes to promo-product relationships"""
    from .services.promo_services import update_products_has_promo_on_m2m_change
    
    if action.startswith("post_"):  # post_add, post_remove, post_clear
        update_products_has_promo_on_m2m_change(instance, action, pk_set)


#CART
class Cart(models.Model):
    cart_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cart'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'Cart'

class CartItem(models.Model):
    cart_item_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cart = models.ForeignKey(
        Cart, 
        on_delete=models.CASCADE,
        related_name='items'
    )
    product = models.ForeignKey(
        'Product',
        on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'CartItems'
        unique_together = [['cart', 'product']]

    def save(self, *args, **kwargs):
        if not self.unit_price:
            self.unit_price = (
                self.product.product_discountedPrice 
                if self.product.product_discountedPrice 
                else self.product.product_price
            )
        super().save(*args, **kwargs)

    @property
    def total_price(self):
        return self.quantity * self.unit_price


#ORDER
class Order(models.Model):
    order_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    order_number = models.CharField(max_length=20, unique=True, editable=False)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True, db_column='user_id')
    order_date = models.DateTimeField(auto_now_add=True)
    order_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    order_status = models.CharField(
        max_length=255,
        choices=[
            ('PENDING', 'Pending'),
            ('CONFIRMED', 'Confirmed'),
            ('SHIPPED', 'Shipped'),
            ('DELIVERED', 'Delivered'),
            ('CANCELLED', 'Cancelled'),
            ('REFUNDED', 'Refunded')
        ],
        default='PENDING'
    )
    is_archived = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.order_number:
            from datetime import datetime
            year = datetime.now().year
            last_order = Order.objects.filter(order_number__startswith=f'OID-{year}').order_by('-created_at').first()
            if last_order and last_order.order_number:
                try:
                    last_num = int(last_order.order_number.split('-')[-1])
                except Exception:
                    last_num = 0
                new_num = last_num + 1
            else:
                new_num = 1
            self.order_number = f'OID-{year}-{new_num:05d}'
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'Orders'


#ORDER ITEMS
class OrderItem(models.Model):
    order_item_id = models.CharField(primary_key=True, max_length=10, unique=True, editable=False)
    order_id = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    quantity = models.IntegerField(default=1)
    total_item_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        from .services.order_services import generate_order_item_id, calculate_order_item_total
        
        if not self.order_item_id:
            last_order_item = OrderItem.objects.order_by('-created_at').first()
            self.order_item_id = generate_order_item_id(last_order_item)
        
        if self.product_id:
            self.total_item_price = calculate_order_item_total(self.product_id, self.quantity)
        
        super().save(*args, **kwargs)
    
    class Meta:
        db_table = 'OrderItems'


#PAYMENT
class Payment(models.Model):
    PAYMENT_METHODS = [
        ('GCASH', 'Gcash'),
        ('PAYMAYA', 'PayMaya'),
        ('COD', 'Cash on Delivery'),
    ]
    PAYMENT_STATUS = [
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
        ('REFUNDED', 'Refunded'),
    ]
    payment_id = models.CharField(primary_key=True, max_length=12, unique=True, editable=False)
    order_id = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='PENDING')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_id = models.CharField(max_length=255, null=True, blank=True)
    payment_date = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.payment_id} - {self.order_id.order_number} - {self.payment_status}"
