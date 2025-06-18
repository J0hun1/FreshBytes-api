from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.utils import timezone


class ProductStatus(models.TextChoices):
    ACTIVE = 'ACTIVE', 'Active'
    INACTIVE = 'INACTIVE', 'Inactive'
    OUT_OF_STOCK = 'OUT_OF_STOCK', 'Out of Stock'
    DISCONTINUED = 'DISCONTINUED', 'Discontinued'

# Create your models here.
class Product(models.Model):
    product_id = models.AutoField(primary_key=True)
    product_name = models.CharField(max_length=255)
    product_price = models.IntegerField(default=0)
    product_brief_description = models.CharField(max_length=255)
    product_full_description = models.CharField(max_length=255)
    product_discountedPrice = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    product_sku = models.CharField(max_length=255)
    product_unit = models.CharField(max_length=50, null=True)
    product_status = models.CharField(max_length=20, choices=ProductStatus.choices, default=ProductStatus.ACTIVE)
    product_location = models.CharField(max_length=255, null=True)
    # user = models.ForeignKey(User, on_delete=models.CASCADE)
    # category = models.ForeignKey(Category, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)
    post_date = models.DateTimeField(null=True)
    harvest_date = models.DateTimeField(null=True)
    is_active = models.BooleanField(default=True)
    # sellers = models.ManyToManyField(Seller, through='ProductSeller')
    discounted_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    is_discounted = models.BooleanField(default=False)
    is_sale = models.BooleanField(default=False)
    is_srp = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    top_rated = models.BooleanField(default=False)
    sell_count = models.IntegerField(default=0)
    offer_start_date = models.DateTimeField(null=True)
    offer_end_date = models.DateTimeField(null=True)
    promo_price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'Products'