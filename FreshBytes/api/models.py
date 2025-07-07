from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.utils import timezone
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.contrib.auth.hashers import make_password
from .services import update_seller_total_products, update_products_has_promo_on_promo_save, update_products_has_promo_on_promo_delete, update_products_has_promo_on_m2m_change

class UserManager(BaseUserManager):
    def create_user(self, user_email, password=None, **extra_fields):
        if not user_email:
            raise ValueError('The Email field must be set')
        user_email = self.normalize_email(user_email)
        user = self.model(user_email=user_email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_password('defaultpassword123')
        user.save(using=self._db)
        return user

    def create_superuser(self, user_email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_admin', True)
        extra_fields.setdefault('role', 'admin')
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(user_email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('admin', 'Admin'),  # Has full access to both Django admin and application features
        ('seller', 'Seller'),  # Can manage their products and sales
        ('customer', 'Customer'),  # Can make purchases and write reviews
    ]

    user_id = models.CharField(primary_key=True, max_length=10, unique=True, editable=False)
    user_name = models.CharField(max_length=255)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    user_email = models.EmailField(unique=True, null=True)  # Keep nullable for regular users
    password = models.CharField(max_length=128, null=True)
    user_phone = models.CharField(max_length=255)
    user_address = models.CharField(max_length=255)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Django's built-in permission flags
    is_active = models.BooleanField(default=True)  # Can login
    is_staff = models.BooleanField(default=False)  # Can access Django admin
    is_superuser = models.BooleanField(default=False)  # Has all permissions
    is_deleted = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'user_email'
    REQUIRED_FIELDS = ['user_name', 'first_name', 'last_name']

    def clean(self):
        """Validate that sellers must have an email"""
        if self.role == 'seller' and not self.user_email:
            from django.core.exceptions import ValidationError
            raise ValidationError('Sellers must have an email address')
        super().clean()

    def save(self, *args, **kwargs):
        self.clean()  # Run validation before saving
        if not self.user_id:
            current_year = timezone.now().year % 100
            last_user = User.objects.order_by('-created_at').first()
            if last_user:
                last_id = int(last_user.user_id[3:6])
                new_id = f"uid{last_id + 1:03d}{current_year:02d}"
            else:
                new_id = f"uid00125"
            self.user_id = new_id

        # Ensure Django admin access for admin role
        if self.role == 'admin':
            self.is_staff = True
            self.is_superuser = True
        
        super().save(*args, **kwargs)

    def __str__(self):
        """Return the user_id as the string representation"""
        return self.user_id

    @property
    def is_admin(self):
        """Property to maintain compatibility - returns True if role is admin"""
        return self.role == 'admin'

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        db_table = 'Users'

#SELLER
class Seller(models.Model):
    seller_id = models.CharField(primary_key=True, max_length=10, unique=True, editable=False)

    def save(self, *args, **kwargs):
        if not self.seller_id:
            last_seller = Seller.objects.order_by('-created_at').first()
            if last_seller:
                last_id = int(last_seller.seller_id[3:6])  # Extract the numeric part after 'sid'
                new_id = f"sid{last_id + 1:03d}25"
            else:
                new_id = "sid00125"
            self.seller_id = new_id
        super().save(*args, **kwargs)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
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
        """Validate seller data before saving"""
        from django.core.exceptions import ValidationError
        if not self.user_id:
            raise ValidationError('A seller must be associated with a user')
        if not self.user_id.user_email:
            raise ValidationError('The associated user must have an email address')
        
    def save(self, *args, **kwargs):
        if not self.seller_id:
            last_seller = Seller.objects.order_by('-created_at').first()
            if last_seller:
                last_id = int(last_seller.seller_id[3:6])  # Extract the numeric part after 'sid'
                new_id = f"sid{last_id + 1:03d}25"
            else:
                new_id = "sid00125"
            self.seller_id = new_id

        # Ensure numeric fields are not null
        self.total_products = self.total_products or 0
        self.total_orders = self.total_orders or 0
        self.total_reviews = self.total_reviews or 0
        self.average_rating = self.average_rating or 0
        self.total_followers = self.total_followers or 0
        self.total_likes = self.total_likes or 0
        self.total_products_sold = self.total_products_sold or 0

        self.clean()  # Run validation
        
        # If business_email is blank, use user's email
        if not self.business_email and self.user_id and self.user_id.user_email:
            self.business_email = self.user_id.user_email
            
        super().save(*args, **kwargs)

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

    def save(self, *args, **kwargs):
        if not self.sub_category_id:
            last_sub_category = SubCategory.objects.order_by('-created_at').first()
            if last_sub_category:
                last_id = int(last_sub_category.sub_category_id[5:8])  # Extract the numeric part after 'subid'
                new_id = f"subid{last_id + 1:03d}25"
            else:
                new_id = "subid00125"
            self.sub_category_id = new_id
        super().save(*args, **kwargs)
    category_id = models.ForeignKey(Category, on_delete=models.CASCADE, null=True)
    sub_category_name = models.CharField(max_length=255, default="", unique=True)
    sub_category_description = models.CharField(max_length=255)
    sub_category_image = models.ImageField(upload_to='sub_category_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    

#PRODUCT 
class ProductStatus(models.TextChoices):
    ROTTEN = 'ROTTEN', 'Rotten'
    SLIGHTLY_WITHERED = 'SLIGHTLY_WITHERED', 'Slightly Withered'
    FRESH = 'FRESH', 'Fresh'
    
class Product(models.Model):
    product_id = models.CharField(primary_key=True, max_length=10, unique=True, editable=False)
    seller_id = models.ForeignKey(Seller, on_delete=models.CASCADE, null=True)
    product_name = models.CharField(max_length=255)
    product_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    product_brief_description = models.CharField(max_length=255)
    product_full_description = models.CharField(max_length=255)
    product_discountedPrice = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    product_sku = models.CharField(max_length=255, unique=True, editable=False)
    product_status = models.CharField(max_length=20, choices=ProductStatus.choices, default=ProductStatus.FRESH)
    product_location = models.CharField(max_length=255, null=True)
    sub_category_id = models.ForeignKey(SubCategory, on_delete=models.CASCADE, null=True)
    has_promo = models.BooleanField(default=False)
    weight = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    quantity = models.IntegerField(default=1)
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

    @property
    def user_id(self):
        return self.seller_id.user_id.user_id if self.seller_id and self.seller_id.user_id else None

    @property
    def category_id(self):
        """Get the category through the subcategory relationship"""
        return self.sub_category_id.category_id if self.sub_category_id else None

    @property
    def discounted_amount(self):
        if self.product_discountedPrice is not None:
            return self.product_price - self.product_discountedPrice
        return None

    def update_discounted_price(self):
        """Update discounted price based on active promos"""
        active_promos = self.promos.filter(
            is_active=True,
            promo_start_date__lte=timezone.now(),
            promo_end_date__gte=timezone.now()
        ).order_by('-discount_amount', '-discount_percentage')

        if not active_promos.exists():
            self.product_discountedPrice = None
            self.is_discounted = False
            self.has_promo = False
            self.save()
            return

        # Get the promo with the highest discount
        best_promo = active_promos.first()
        
        if best_promo.discount_type == Discount_Type.PERCENTAGE:
            discount = (self.product_price * best_promo.discount_percentage) / 100
        else:  # FIXED amount
            discount = best_promo.discount_amount

        self.product_discountedPrice = max(0, self.product_price - discount)
        self.is_discounted = True
        self.has_promo = True
        self.save()

    def generate_sku(self, counter=0):
        """Generate a unique SKU with optional counter for conflict resolution"""
        prefix = self.product_name[:3].upper() if len(self.product_name) >= 3 else self.product_name.upper()
        seller_products_count = Product.objects.filter(seller_id=self.seller_id).count() + 1
        seller_id_suffix = self.seller_id.seller_id[-5:] if self.seller_id and len(self.seller_id.seller_id) >= 5 else "00000"
        
        # Add counter to SKU if there's a conflict
        if counter > 0:
            return f"{prefix}{seller_products_count:03d}{seller_id_suffix}_{counter}"
        return f"{prefix}{seller_products_count:03d}{seller_id_suffix}"

    def save(self, *args, **kwargs):
        if not self.product_id:
            last_product = Product.objects.order_by('-created_at').first()
            if last_product and last_product.product_id and len(last_product.product_id) >= 8:
                try:
                    last_id = int(last_product.product_id[4:7])
                    new_id = f"prod{last_id + 1:03d}25"
                except (ValueError, IndexError):
                    new_id = "prod00125"
            else:
                new_id = "prod00125"
            self.product_id = new_id

        # Generate unique SKU
        if not self.product_sku:
            counter = 0
            while True:
                try:
                    self.product_sku = self.generate_sku(counter)
                    # Try saving to check for conflicts
                    if not Product.objects.filter(product_sku=self.product_sku).exists():
                        break
                    counter += 1
                except Exception:
                    counter += 1
                # Prevent infinite loop
                if counter > 1000:
                    raise ValueError("Unable to generate unique SKU after 1000 attempts")

        if self.product_price > 0 and (self.product_discountedPrice is None or self.product_discountedPrice <= 0):
            self.is_srp = True

        super().save(*args, **kwargs)

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

    def save(self, *args, **kwargs):
        if not self.review_id:
            current_year = timezone.now().year % 100  # Get last two digits of the current year
            last_review = Reviews.objects.order_by('-created_at').first()
            if last_review:
                last_id = int(last_review.review_id[3:6])  # Extract the numeric part after 'rid'
                new_id = f"rid{last_id + 1:03d}{current_year:02d}"
            else:
                new_id = f"rid001{current_year:02d}"
            self.review_id = new_id
        super().save(*args, **kwargs)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    review_rating = models.IntegerField(default=0)
    review_comment = models.CharField(max_length=255)
    review_date = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'Reviews'


#PROMO
class Discount_Type(models.TextChoices):
    PERCENTAGE = 'PERCENTAGE', 'Percentage'
    FIXED = 'FIXED', 'Fixed'

class Promo(models.Model):
    promo_id = models.CharField(primary_key=True, max_length=10, unique=True, editable=False)
    seller_id = models.ForeignKey(Seller, on_delete=models.CASCADE, default=None)
    product_id = models.ManyToManyField(Product, related_name='promos')
    promo_description = models.CharField(max_length=255, default="")
    promo_name = models.CharField(max_length=255)
    discount_type = models.CharField(max_length=255, choices=Discount_Type.choices, default=Discount_Type.FIXED)
    discount_amount = models.IntegerField(default=0)
    discount_percentage = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    promo_start_date = models.DateTimeField(default=timezone.now)
    promo_end_date = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.promo_id:
            last_promo = Promo.objects.order_by('-created_at').first()
            if last_promo:
                last_id = int(last_promo.promo_id[3:6])
                new_id = f"pid{last_id + 1:03d}25"
            else:
                new_id = "pid00125"
            self.promo_id = new_id

        # Ensure end date is after start date
        if self.promo_end_date <= self.promo_start_date:
            self.promo_end_date = self.promo_start_date + timezone.timedelta(days=7)

        super().save(*args, **kwargs)

        # Update discounted prices for all linked products
        for product in self.product_id.all():
            product.update_discounted_price()

    class Meta:
        db_table = 'Promo'


# Signal handlers for Promo-Product relationship
@receiver(post_save, sender=Promo)
def update_product_prices_on_promo_save(sender, instance, created, **kwargs):
    """Update product prices when a promo is created or updated"""
    for product in instance.product_id.all():
        product.update_discounted_price()

@receiver(post_delete, sender=Promo)
def update_product_prices_on_promo_delete(sender, instance, **kwargs):
    """Update product prices when a promo is deleted"""
    for product in instance.product_id.all():
        product.update_discounted_price()

@receiver(models.signals.m2m_changed, sender=Promo.product_id.through)
def update_product_prices_on_m2m_change(sender, instance, action, pk_set, **kwargs):
    """Update product prices when products are added/removed from a promo"""
    if action in ["post_add", "post_remove", "post_clear"]:
        # Update new products
        if pk_set:
            products = Product.objects.filter(pk__in=pk_set)
            for product in products:
                product.update_discounted_price()
        
        # For post_remove and post_clear, also update previously linked products
        if action in ["post_remove", "post_clear"]:
            for product in instance.product_id.all():
                product.update_discounted_price()


#CART
class Cart(models.Model):
    cart_id = models.CharField(primary_key=True, max_length=10, unique=True, editable=False)

    def save(self, *args, **kwargs):
        if not self.cart_id:
            last_cart = Cart.objects.order_by('-created_at').first()
            if last_cart:
                last_id = int(last_cart.cart_id[3:6])  # Extract the numeric part after 'cid'
                new_id = f"cid{last_id + 1:03d}25"
            else:
                new_id = "cid00125"
            self.cart_id = new_id
        super().save(*args, **kwargs)
        
    user_id = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

#CART ITEMS
class CartItem(models.Model):
    cart_item_id = models.CharField(primary_key=True, max_length=12, unique=True, editable=False)
    cart_id = models.ForeignKey(Cart, on_delete=models.CASCADE, null=True)
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    quantity = models.IntegerField(default=1)
    total_item_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_percentage = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.cart_item_id:
            last_cart_item = CartItem.objects.order_by('-created_at').first()
            if last_cart_item and last_cart_item.cart_item_id and len(last_cart_item.cart_item_id) >= 8:
                try:
                    last_id = int(last_cart_item.cart_item_id[5:8])  # Extract the numeric part after 'citid'
                    new_id = f"citid{last_id + 1:03d}25"
                except (ValueError, IndexError):
                    new_id = "citid00125"
            else:
                new_id = "citid00125"
            self.cart_item_id = new_id
        
        # Calculate total_price before saving
        if self.product_id:
            product_price = self.product_id.product_discountedPrice if self.product_id.is_discounted else self.product_id.product_price
            self.total_item_price = product_price * self.quantity
        
        super().save(*args, **kwargs)


#ORDER
class OrderStatus(models.TextChoices):
    PENDING = 'PENDING', 'Pending'
    CONFIRMED = 'CONFIRMED', 'Confirmed'
    SHIPPED = 'SHIPPED', 'Shipped'
    DELIVERED = 'DELIVERED', 'Delivered'
    CANCELLED = 'CANCELLED', 'Cancelled'
    REFUNDED = 'REFUNDED', 'Refunded'

class Order(models.Model):
    order_id = models.CharField(primary_key=True, max_length=10, unique=True, editable=False)
    
    def save(self, *args, **kwargs):
        if not self.order_id:
            last_order = Order.objects.order_by('-created_at').first()
            if last_order:
                last_id = int(last_order.order_id[7:10])  # Extract the numeric part after 'orderid'
                new_id = f"oid{last_id + 1:03d}25"
            else:
                new_id = "oid00125"
            self.order_id = new_id
        super().save(*args, **kwargs)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    order_date = models.DateTimeField(auto_now_add=True)
    order_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_percentage = models.IntegerField(default=0)
    order_status = models.CharField(max_length=255, choices=OrderStatus.choices, default=OrderStatus.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'Orders'


#ORDER ITEMS
class OrderItem(models.Model):
    order_item_id = models.CharField(primary_key=True, max_length=10, unique=True, editable=False)
    order_id = models.ForeignKey(Order, on_delete=models.CASCADE, null=True)
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    quantity = models.IntegerField(default=1)
    total_item_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.order_item_id:
            last_order_item = OrderItem.objects.order_by('-created_at').first()
            if last_order_item and last_order_item.order_item_id and len(last_order_item.order_item_id) >= 8:
                try:
                    last_id = int(last_order_item.order_item_id[5:8])  # Extract the numeric part after 'oitid'
                    new_id = f"oitid{last_id + 1:03d}25"
                except (ValueError, IndexError):
                    new_id = "oitid00125"
            else:
                new_id = "oitid00125"
            self.order_item_id = new_id
        
        # Calculate total_item_price before saving
        if self.product_id:
            product_price = self.product_id.product_discountedPrice if self.product_id.is_discounted else self.product_id.product_price
            self.total_item_price = product_price * self.quantity
        
        super().save(*args, **kwargs)
    
    class Meta:
        db_table = 'OrderItems'


#ORDER STATUS



#PAYMENT