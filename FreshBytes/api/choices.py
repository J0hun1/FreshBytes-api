from django.db import models

class ProductStatus(models.TextChoices):
    ROTTEN = 'ROTTEN', 'Rotten'
    SLIGHTLY_WITHERED = 'SLIGHTLY_WITHERED', 'Slightly Withered'
    FRESH = 'FRESH', 'Fresh'

class Discount_Type(models.TextChoices):
    PERCENTAGE = 'PERCENTAGE', 'Percentage'
    FIXED = 'FIXED', 'Fixed'

class OrderStatus(models.TextChoices):
    PENDING = 'PENDING', 'Pending'
    CONFIRMED = 'CONFIRMED', 'Confirmed'
    SHIPPED = 'SHIPPED', 'Shipped'
    DELIVERED = 'DELIVERED', 'Delivered'
    CANCELLED = 'CANCELLED', 'Cancelled'
    REFUNDED = 'REFUNDED', 'Refunded' 