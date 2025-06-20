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
    category_name = models.CharField(max_length=255, unique=True)
    category_description = models.CharField(max_length=255, default="")
    category_isActive = models.BooleanField(default=True)
    category_image = models.ImageField(upload_to='category_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'Categories'

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
    sub_category_id = models.ForeignKey(SubCategory, on_delete=models.CASCADE, null=True)
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

class Discount_Type(models.TextChoices):
    PERCENTAGE = 'PERCENTAGE', 'Percentage'
    FIXED = 'FIXED', 'Fixed'

class Promo(models.Model):
    promo_id = models.CharField(primary_key=True, max_length=12, unique=True, editable=False)
    seller_id = models.ForeignKey(Seller, on_delete=models.CASCADE, null=True)

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

class Promo_Details(models.Model):
    promo_details_id = models.CharField(primary_key=True, max_length=12, unique=True, editable=False)
    promo_id = models.ForeignKey(Promo, on_delete=models.CASCADE, null=True)

    def save(self, *args, **kwargs):
        if not self.promo_details_id:
            last_promo_details = Promo_Details.objects.order_by('-created_at').first()
            if last_promo_details:
                last_id = int(last_promo_details.promo_details_id[3:6])  # Extract the numeric part after 'ptid'
                new_id = f"ptid{last_id + 1:03d}25"
            else:
                new_id = "ptid00125"
            self.promo_details_id = new_id
        super().save(*args, **kwargs)
    

    def save(self, *args, **kwargs):
        if not self.promo_code:
            last_promo_details = Promo_Details.objects.order_by('-created_at').first()
            if last_promo_details:
                last_code = int(last_promo_details.promo_code[-3:])  # Extract the numeric part at the end
                new_code = f"PC{last_code + 1:03d}"
            else:
                new_code = "PC001"
            self.promo_code = new_code
        super().save(*args, **kwargs)
    
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'Promo_Details'
