
from django.db.models import F

def update_seller_total_products(seller):
    """
    Recalculates and updates the total_products count for a given seller.
    """
    if seller:
        product_count = seller.product_set.count()
        print(f"Service: Updating seller {seller} total_products to {product_count}")
        seller.total_products = product_count
        seller.save(update_fields=['total_products'])

def generate_seller_id(last_seller):
    """Generate unique seller ID"""
    if last_seller:
        last_id = int(last_seller.seller_id[3:6])
        return f"sid{last_id + 1:03d}25"
    return "sid00125"

def validate_seller(seller):
    """Validate seller data"""
    from django.core.exceptions import ValidationError
    
    if not seller.user_id:
        raise ValidationError('A seller must be associated with a user')
    if not seller.user_id.user_email:
        raise ValidationError('The associated user must have an email address')

def initialize_seller_stats(seller):
    """Initialize seller statistics with default values"""
    seller.total_products = seller.total_products or 0
    seller.total_orders = seller.total_orders or 0
    seller.total_reviews = seller.total_reviews or 0
    seller.average_rating = seller.average_rating or 0
    seller.total_followers = seller.total_followers or 0
    seller.total_likes = seller.total_likes or 0
    seller.total_products_sold = seller.total_products_sold or 0

def update_seller_total_orders(seller):
    """
    Recalculates and updates the total_orders count for a given seller.
    """
    from ..models import OrderItem
    order_ids = OrderItem.objects.filter(
        product_id__seller_id=seller
    ).values_list('order_id', flat=True).distinct()
    seller.total_orders = len(order_ids)
    seller.save(update_fields=['total_orders'])