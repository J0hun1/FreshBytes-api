from django.db import models
import uuid
from .order import Order

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

    class Meta:
        db_table = 'Payments' 