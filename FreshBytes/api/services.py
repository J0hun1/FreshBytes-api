from django.db.models import F

#SELLER LOGIC

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


#PRODUCT-PROMO LOGIC

def update_product_has_promo_field(product):
    """
    Updates the has_promo field for a given product based on active promos.
    """
    from .models import Promo
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

#PROMO LOGIC
def update_products_has_promo_on_promo_save(promo):
    """
    Updates has_promo field for all products associated with a promo when the promo is saved.
    """
    products = promo.product_id.all()
    
    for product in products:
        update_product_has_promo_field(product)



def update_products_has_promo_on_m2m_change(promo, action, pk_set=None):
    """
    Updates has_promo field when products are added/removed from a promo.
    """
    from .models import Product
    
    if action == "post_clear":
        # All products were removed, so we need to update all products that were in this promo
        products = promo.product_id.all()
    else:
        # Get the specific products that were added/removed
        products = Product.objects.filter(pk__in=pk_set)
    
    for product in products:
        update_product_has_promo_field(product)


#CART LOGIC

def update_cart_total_price(cart):
    """
    Updates the total_price for a given cart.
    """
    cart_items = cart.cartitem_set.all()
    total_price = sum(item.total_price for item in cart_items)
    cart.total_price = total_price
    cart.save(update_fields=['total_price'])

