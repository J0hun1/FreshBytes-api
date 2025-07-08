def update_product_has_promo_field(product):
    """
    Updates the has_promo field of a product based on its active promos.
    """
    has_active_promos = product.promos.filter(is_active=True).exists()
    product.has_promo = has_active_promos
    product.save()

def update_products_has_promo_on_promo_save(promo):
    """
    Updates has_promo field for all products associated with a promo when the promo is saved.
    """
    products = promo.product_id.all()
    
    for product in products:
        update_product_has_promo_field(product)


def update_products_has_promo_on_promo_delete(promo):
    """
    Updates has_promo field for all products when a promo is deleted.
    """
    products = promo.product_id.all()
    for product in products:
        update_product_has_promo_field(product)


def update_products_has_promo_on_m2m_change(promo, action, pk_set=None):
    """
    Updates has_promo field when products are added/removed from a promo.
    """
    from ..models import Product
    
    if action == "post_clear":
        # All products were removed, so we need to update all products that were in this promo
        products = promo.product_id.all()
    else:
        # Get the specific products that were added/removed
        products = Product.objects.filter(pk__in=pk_set)
    
    for product in products:
        update_product_has_promo_field(product)