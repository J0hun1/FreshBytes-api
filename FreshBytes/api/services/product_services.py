def update_product_has_promo_field(product):
    """
    Updates the has_promo field for a given product based on active promos.
    """
    from ...api.models import Promo
    active_promos = Promo.objects.filter(
        product_id=product,
        is_active=True
    ).exists()
    
    product.has_promo = active_promos
    product.save(update_fields=['has_promo'])

def update_products_has_promo_on_promo_delete(promo):
    """
    Updates has_promo field for all products that were associated with a deleted promo.
    """
    products = promo.product_id.all()
    
    for product in products:
        update_product_has_promo_field(product)

def update_seller_total_products(seller):
    """
    Updates the total_products count for a seller based on their active products.
    """
    total_products = seller.product_set.filter(is_deleted=False).count()
    seller.total_products = total_products
    seller.save()