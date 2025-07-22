from django.db import models
from django.utils import timezone
import uuid
from .seller import Seller
from .product import Product

class PromoProduct(models.Model):
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
        from ..services.promo_services import update_products_has_promo_on_promo_save
        # Ensure end date is after start date
        if self.promo_end_date <= self.promo_start_date:
            self.promo_end_date = self.promo_start_date + timezone.timedelta(days=7)
        super().save(*args, **kwargs)
        update_products_has_promo_on_promo_save(self)

    class Meta:
        db_table = 'Promo'

# Signal handlers for Promo-Product relationship
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from ..services.promo_services import update_products_has_promo_on_promo_save, update_products_has_promo_on_promo_delete, update_products_has_promo_on_m2m_change

@receiver(post_save, sender=Promo)
def handle_promo_save(sender, instance, created, **kwargs):
    if not kwargs.get('raw', False):
        update_products_has_promo_on_promo_save(instance)

@receiver(pre_delete, sender=Promo)
def handle_promo_pre_delete(sender, instance, **kwargs):
    update_products_has_promo_on_promo_delete(instance)

@receiver(models.signals.m2m_changed, sender=Promo.product_id.through)
def handle_promo_m2m_changes(sender, instance, action, pk_set, **kwargs):
    if action.startswith("post_"):  # post_add, post_remove, post_clear
        update_products_has_promo_on_m2m_change(instance, action, pk_set)
