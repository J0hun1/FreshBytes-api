from django.db import models
from django.utils import timezone
import uuid
from .user import User
from .product import Product

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

class OrderItem(models.Model):
    order_item_id = models.CharField(primary_key=True, max_length=10, unique=True, editable=False)
    order_id = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    quantity = models.IntegerField(default=1)
    total_item_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        from ..services.order_services import generate_order_item_id, calculate_order_item_total
        if not self.order_item_id:
            last_order_item = OrderItem.objects.order_by('-created_at').first()
            self.order_item_id = generate_order_item_id(last_order_item)
        if self.product_id:
            self.total_item_price = calculate_order_item_total(self.product_id, self.quantity)
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'OrderItems'
