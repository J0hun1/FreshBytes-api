from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.utils import timezone
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .services import update_seller_total_products

#USER
class User(models.Model):
    user_id = models.CharField(primary_key=True, max_length=5, unique=True, editable=False)

    def save(self, *args, **kwargs):
        if not self.user_id:
            current_year = timezone.now().year % 100  # Get last two digits of the current year
            last_user = User.objects.order_by('-created_at').first()
            if last_user:
                last_id = int(last_user.user_id[3:6])  # Extract the numeric part after 'uid'
                new_id = f"uid{last_id + 1:03d}{current_year:02d}"
            else:
                new_id = f"uid00125"
            self.user_id = new_id
        super().save(*args, **kwargs)
    user_name = models.CharField(max_length=255)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    user_email = models.EmailField(unique=True)
    user_password = models.CharField(max_length=255)
    user_phone = models.CharField(max_length=255)
    user_address = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    
#SELLER
class Seller(models.Model):
    seller_id = models.CharField(primary_key=True, max_length=8, unique=True, editable=False)

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
    business_email = models.EmailField(default="")
    business_phone = models.IntegerField(default="")
    business_address = models.CharField(default="", max_length=255, null=True)
    total_earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)
    total_products = models.IntegerField(default=0, null=True)
    total_orders = models.IntegerField(default=0, null=True)
    total_reviews = models.IntegerField(default=0, null=True)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0, null=True)
    total_followers = models.IntegerField(default=0, null=True)
    total_products_sold = models.IntegerField(default=0, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)


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
        db_table = 'Categories'

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
    SLIGHTLY_WILTED = 'SLIGHTLY_WILTED', 'Slightly Wilted'
    FRESH = 'FRESH', 'Fresh'
    
class Product(models.Model):
    product_id = models.CharField(primary_key=True, max_length=8, unique=True, editable=False)

    def save(self, *args, **kwargs):
        if not self.product_id:
            last_product = Product.objects.order_by('-created_at').first()
            if last_product and last_product.product_id and len(last_product.product_id) >= 8:
                try:
                    last_id = int(last_product.product_id[4:7])  # Extract the numeric part after 'prod'
                    new_id = f"prod{last_id + 1:03d}25"
                except (ValueError, IndexError):
                    new_id = "prod00125"
            else:
                new_id = "prod00125"
            self.product_id = new_id
        
        # Set is_srp flag
        if self.product_price > 0 and (self.product_discountedPrice is None or self.product_discountedPrice <= 0):
            self.is_srp = True
        
        # Set is_discounted flag
        if self.discounted_amount is not None and self.discounted_amount > 0:
            self.is_discounted = True
            
        super().save(*args, **kwargs)
        
    @property
    def user_id(self):
        return self.seller_id.user_id.user_id if self.seller_id and self.seller_id.user_id else None


    seller_id = models.ForeignKey(Seller, on_delete=models.CASCADE, null=True)
    product_name = models.CharField(max_length=255)
    product_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    product_brief_description = models.CharField(max_length=255)
    product_full_description = models.CharField(max_length=255)
    product_discountedPrice = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    product_sku = models.CharField(max_length=255)
    product_status = models.CharField(max_length=20, choices=ProductStatus.choices, default=ProductStatus.FRESH)
    product_location = models.CharField(max_length=255, null=True)
    category_id = models.ForeignKey(Category, on_delete=models.CASCADE, null=True)
    sub_category_id = models.ForeignKey(SubCategory, on_delete=models.CASCADE, null=True)
    has_promo = models.BooleanField(default=False)
    weight = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    quantity = models.IntegerField(default=1)
    post_date = models.DateTimeField(default=timezone.now)
    harvest_date = models.DateTimeField(null=True)
    is_active = models.BooleanField(default=True)
    review_count = models.IntegerField(default=0)
    top_rated = models.BooleanField(default=False)
    

    @property
    def discounted_amount(self):
        if self.product_discountedPrice is not None:
            return self.product_price - self.product_discountedPrice
        return None
    
    is_srp = models.BooleanField(default=False)
    is_discounted = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    
    sell_count = models.IntegerField(default=0)
    offer_start_date = models.DateTimeField(null=True)
    offer_end_date = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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
    review_id = models.CharField(primary_key=True, max_length=12, unique=True, editable=False)

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
    promo_id = models.CharField(primary_key=True, max_length=12, unique=True, editable=False)
    seller_id = models.ForeignKey(Seller, on_delete=models.CASCADE, default=None)
    product_id = models.ManyToManyField(Product, related_name='promos')

    def save(self, *args, **kwargs):
        if not self.promo_id:
            last_promo = Promo.objects.order_by('-created_at').first()
            if last_promo:
                last_id = int(last_promo.promo_id[3:6])  # Extract the numeric part after 'pid'
                new_id = f"pid{last_id + 1:03d}25"
            else:
                new_id = "pid00125"
            self.promo_id = new_id
        super().save(*args, **kwargs)
    promo_description = models.CharField(max_length=255, default="")
    promo_name = models.CharField(max_length=255)
    discount_type = models.CharField(max_length=255, choices=Discount_Type.choices, default=Discount_Type.FIXED)
    discount_amount = models.IntegerField(default=0)
    discount_percentage = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    promo_start_date = models.DateTimeField(null=True)
    promo_end_date = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'Promo'

# Signals to automatically update has_promo field on products
@receiver(post_save, sender=Promo)
def update_product_has_promo_on_save(sender, instance, created, **kwargs):
    """Update has_promo field when a promo is created or updated"""
    # Get all products associated with this promo
    products = instance.product_id.all()
    
    for product in products:
        # Check if there are any active promos for this product
        active_promos = Promo.objects.filter(
            product_id=product,
            is_active=True
        ).exists()
        
        # Update the product's has_promo field
        product.has_promo = active_promos
        product.save(update_fields=['has_promo'])

@receiver(post_delete, sender=Promo)
def update_product_has_promo_on_delete(sender, instance, **kwargs):
    """Update has_promo field when a promo is deleted"""
    # Get all products that were associated with this promo
    products = instance.product_id.all()
    
    for product in products:
        # Check if there are any remaining active promos for this product
        active_promos = Promo.objects.filter(
            product_id=product,
            is_active=True
        ).exists()
        
        # Update the product's has_promo field
        product.has_promo = active_promos
        product.save(update_fields=['has_promo'])

# Signal to handle many-to-many relationship changes
@receiver(models.signals.m2m_changed, sender=Promo.product_id.through)
def update_product_has_promo_on_m2m_change(sender, instance, action, pk_set, **kwargs):
    """Update has_promo field when products are added/removed from a promo"""
    if action in ["post_add", "post_remove", "post_clear"]:
        # Get all affected products
        if action == "post_clear":
            # All products were removed, so we need to update all products that were in this promo
            products = instance.product_id.all()
        else:
            # Get the specific products that were added/removed
            products = Product.objects.filter(pk__in=pk_set)
        
        for product in products:
            # Check if there are any active promos for this product
            active_promos = Promo.objects.filter(
                product_id=product,
                is_active=True
            ).exists()
            
            # Update the product's has_promo field
            product.has_promo = active_promos
            product.save(update_fields=['has_promo'])


