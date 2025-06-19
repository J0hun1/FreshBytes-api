from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.utils import timezone


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
    business_email = models.EmailField(default="", unique=True)
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

class Category(models.Model):
    category_id = models.AutoField(primary_key=True)
    category_name = models.CharField(max_length=255)
    category_isActive = models.BooleanField(default=True)
    category_image = models.ImageField(upload_to='category_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'Categories'

class SubCategory(models.Model):
    category_id = models.ForeignKey(Category, on_delete=models.CASCADE, null=True)
    sub_category_id = models.AutoField(primary_key=True)
    sub_category_name = models.CharField(max_length=255, default="", unique=True)
    sub_category_description = models.CharField(max_length=255)
    sub_category_image = models.ImageField(upload_to='sub_category_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    

class ProductStatus(models.TextChoices):
    ACTIVE = 'ACTIVE', 'Active'
    INACTIVE = 'INACTIVE', 'Inactive'
    OUT_OF_STOCK = 'OUT_OF_STOCK', 'Out of Stock'
    DISCONTINUED = 'DISCONTINUED', 'Discontinued'

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
    product_status = models.CharField(max_length=20, choices=ProductStatus.choices, default=ProductStatus.ACTIVE)
    product_location = models.CharField(max_length=255, null=True)
    category_id = models.ForeignKey(Category, on_delete=models.CASCADE, null=True)
    quantity = models.IntegerField(default=1)
    post_date = models.DateTimeField(default=timezone.now)
    harvest_date = models.DateTimeField(null=True)
    is_active = models.BooleanField(default=True)
    

    @property
    def discounted_amount(self):
        if self.product_discountedPrice is not None:
            return self.product_price - self.product_discountedPrice
        return None
    
    is_srp = models.BooleanField(default=False)
    is_discounted = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    top_rated = models.BooleanField(default=False)
    sell_count = models.IntegerField(default=0)
    offer_start_date = models.DateTimeField(null=True)
    offer_end_date = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'Products'