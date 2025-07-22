from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator
import uuid
from .seller import Seller
from .category import SubCategory

class ProductManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)

class Product(models.Model):
    product_id = models.CharField(primary_key=True, max_length=36, unique=True, editable=False, default=uuid.uuid4)
    seller_id = models.ForeignKey(Seller, on_delete=models.CASCADE, null=True)
    product_name = models.CharField(max_length=255)
    product_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0.01)])
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
    weight = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0.01)])
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
            from ..services.product_services import update_product_discounted_price
            self._skip_update = True  # Set flag to prevent recursion
            try:
                update_product_discounted_price(self)
            finally:
                self._skip_update = False  # Reset flag

    def save(self, *args, **kwargs):
        from ..services.product_services import generate_product_sku
        is_new = not self.pk  # Check if this is a new product
        if not self.product_sku:
            try:
                self.product_sku = generate_product_sku(self)
            except Exception:
                pass  # leave blank if generator fails
        if self.product_price > 0 and (self.product_discountedPrice is None or self.product_discountedPrice <= 0):
            self.is_srp = True
        super().save(*args, **kwargs)
        if not is_new and not self._skip_update and 'update_fields' not in kwargs:
            self.update_discounted_price()

    def delete(self, using=None, keep_parents=False):
        self.is_deleted = True
        self.save()

    class Meta:
        db_table = 'Products'

# Signals for updating seller product count
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from ..services.product_services import update_seller_total_products

@receiver(post_save, sender=Product)
def update_seller_product_count_on_save(sender, instance, **kwargs):
    if instance.seller_id:
        update_seller_total_products(instance.seller_id)

@receiver(post_delete, sender=Product)
def update_seller_product_count_on_delete(sender, instance, **kwargs):
    if instance.seller_id:
        update_seller_total_products(instance.seller_id)
