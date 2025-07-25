from django.db import models
import uuid
from .user import User

class Seller(models.Model):
    seller_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    user_id = models.OneToOneField(User, on_delete=models.CASCADE, related_name='seller_profile', db_column='user_id', null=True, blank=True)
    business_name = models.CharField(default="", max_length=255)
    business_email = models.EmailField(blank=True)
    business_phone = models.IntegerField(default="")
    street = models.CharField(max_length=255, blank=True, null=True)
    barangay = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    province = models.CharField(max_length=255, blank=True, null=True)
    zip_code = models.CharField(max_length=10, blank=True, null=True)
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
    terms_accepted = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)

    def clean(self):
        from ..services.seller_services import validate_seller
        validate_seller(self)
        
    def save(self, *args, **kwargs):
        from ..services.seller_services import initialize_seller_stats
        
        initialize_seller_stats(self)
        self.clean()
        
        if not self.business_email and self.user_id and self.user_id.user_email:
            self.business_email = self.user_id.user_email
            
        super().save(*args, **kwargs)

    def get_customers(self):
        """
        Returns a queryset of unique customers who have bought from this seller.
        """
        from .order import OrderItem
        customer_ids = OrderItem.objects.filter(
            product_id__seller_id=self,
            order_id__order_status='DELIVERED'
        ).values_list('order_id__user_id', flat=True).distinct()
        return User.objects.filter(user_id__in=customer_ids)

    def get_transactions(self):
        """
        Returns a queryset of all orders (transactions) involving this seller.
        """
        from .order import OrderItem, Order
        order_ids = OrderItem.objects.filter(
            product_id__seller_id=self
        ).values_list('order_id', flat=True).distinct()
        return Order.objects.filter(order_id__in=order_ids)

    def get_products_bought_by_customer(self, customer):
        """
        Returns a queryset of products bought by a specific customer from this seller.
        """
        from .order import OrderItem
        from .product import Product
        product_ids = OrderItem.objects.filter(
            product_id__seller_id=self,
            order_id__user_id=customer,
            order_id__order_status='DELIVERED'
        ).values_list('product_id', flat=True).distinct()
        return Product.objects.filter(product_id__in=product_ids)
    

    class Meta:
        db_table = 'Seller'
