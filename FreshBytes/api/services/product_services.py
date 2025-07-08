from django.utils import timezone

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

def generate_product_id(last_product):
    """Generate unique product ID"""
    if last_product and last_product.product_id and len(last_product.product_id) >= 8:
        try:
            last_id = int(last_product.product_id[4:7])
            return f"prod{last_id + 1:03d}25"
        except (ValueError, IndexError):
            return "prod00125"
    return "prod00125"

def generate_product_sku(product, seller_products_count, counter=0):
    """Generate unique SKU for product"""
    prefix = product.product_name[:3].upper() if len(product.product_name) >= 3 else product.product_name.upper()
    seller_id_suffix = product.seller_id.seller_id[-5:] if product.seller_id and len(product.seller_id.seller_id) >= 5 else "00000"
    
    if counter > 0:
        return f"{prefix}{seller_products_count:03d}{seller_id_suffix}_{counter}"
    return f"{prefix}{seller_products_count:03d}{seller_id_suffix}"

def update_product_discounted_price(product):
    """Update product's discounted price based on active promos"""
    from ..models import Discount_Type
    
    active_promos = product.promos.filter(
        is_active=True,
        promo_start_date__lte=timezone.now(),
        promo_end_date__gte=timezone.now()
    ).order_by('-discount_amount', '-discount_percentage')

    if not active_promos.exists():
        product.product_discountedPrice = None
        product.is_discounted = False
        product.has_promo = False
        product.save()
        return

    best_promo = active_promos.first()
    
    if best_promo.discount_type == Discount_Type.PERCENTAGE:
        discount = (product.product_price * best_promo.discount_percentage) / 100
    else:  # FIXED amount
        discount = best_promo.discount_amount

    product.product_discountedPrice = max(0, product.product_price - discount)
    product.is_discounted = True
    product.has_promo = True
    product.save()