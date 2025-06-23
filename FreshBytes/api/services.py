from django.db.models import F

def update_seller_total_products(seller):
    """
    Recalculates and updates the total_products count for a given seller.
    """
    from .models import Seller
    if seller:
        product_count = seller.product_set.count()
        print(f"Service: Updating seller {seller} total_products to {product_count}")
        seller.total_products = product_count
        seller.save(update_fields=['total_products'])

