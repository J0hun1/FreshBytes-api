from django.utils import timezone
from django.db.models import Q
from django.db import transaction
import logging

logger = logging.getLogger(__name__)

def update_product_has_promo_field(product):
    """
    Updates the has_promo field of a product based on its active promos.
    """
    try:
        with transaction.atomic():
            has_active_promos = product.promos.filter(
                is_active=True,
                promo_start_date__lte=timezone.now(),
                promo_end_date__gte=timezone.now()
            ).exists()
            
            # Always update discounted price first
            update_product_discounted_price(product)
            
            if has_active_promos != product.has_promo:
                product.has_promo = has_active_promos
                product.save(update_fields=['has_promo'])
    except Exception as e:
        logger.error(f"Error updating promo field for product {product.product_id}: {str(e)}")
        raise

def update_product_discounted_price(product):
    """
    Updates a product's discounted price based on its active promos.
    Returns True if price was updated, False otherwise.
    """
    try:
        with transaction.atomic():
            from ..models import Discount_Type
            
            active_promos = product.promos.select_related('seller_id').filter(
                Q(is_active=True) &
                Q(promo_start_date__lte=timezone.now()) &
                Q(promo_end_date__gte=timezone.now())
            ).order_by('-discount_amount', '-discount_percentage')

            # Reset discount if no active promos
            if not active_promos.exists():
                if product.is_discounted or product.product_discountedPrice is not None:
                    logger.info(f"Removing discount from product {product.product_id}")
                    product.product_discountedPrice = None
                    product.is_discounted = False
                    product.has_promo = False
                    product.save(update_fields=['product_discountedPrice', 'is_discounted', 'has_promo'])
                return False

            # Get best promo and calculate discount
            best_promo = active_promos.first()
            original_price = product.product_price
            
            if best_promo.discount_type == Discount_Type.PERCENTAGE:
                discount = (original_price * best_promo.discount_percentage) / 100
            else:  # FIXED amount
                discount = best_promo.discount_amount

            new_discounted_price = max(0, original_price - discount)
            
            # Update if price changed or flags need updating
            if (product.product_discountedPrice != new_discounted_price or 
                not product.is_discounted or 
                not product.has_promo):
                logger.info(
                    f"Updating product {product.product_id} discount: "
                    f"Original price: {original_price}, "
                    f"New discounted price: {new_discounted_price}, "
                    f"Promo: {best_promo.promo_id}"
                )
                product.product_discountedPrice = new_discounted_price
                product.is_discounted = True
                product.has_promo = True
                product.save(update_fields=['product_discountedPrice', 'is_discounted', 'has_promo'])
                return True
            
            return False
    except Exception as e:
        logger.error(f"Error updating product {product.product_id} discount: {str(e)}")
        raise

def update_products_has_promo_on_promo_save(promo):
    """
    Updates has_promo field for all products associated with a promo when the promo is saved.
    """
    try:
        with transaction.atomic():
            products = promo.product_id.all()
            logger.info(f"Updating {products.count()} products for promo {promo.promo_id}")
            
            # Force immediate update of all products
            for product in products:
                update_product_discounted_price(product)
                product.refresh_from_db()  # Ensure we have latest data
    except Exception as e:
        logger.error(f"Error updating products for promo {promo.promo_id}: {str(e)}")
        raise

def update_products_has_promo_on_promo_delete(promo):
    """
    Updates all discount-related fields for all products when a promo is deleted.
    """
    try:
        with transaction.atomic():
            # Get all affected products before deletion
            products = list(promo.product_id.all())  # Convert to list to avoid query after deletion
            logger.info(f"Removing promo {promo.promo_id} from {len(products)} products")
            
            # Update each product's discount fields
            for product in products:
                # This will recalculate discounts based on remaining active promos
                update_product_discounted_price(product)
                product.refresh_from_db()  # Ensure we have latest data
                
                # Double-check if product still has any active promos
                has_other_active_promos = product.promos.filter(
                    is_active=True,
                    promo_start_date__lte=timezone.now(),
                    promo_end_date__gte=timezone.now()
                ).exclude(promo_id=promo.promo_id).exists()
                
                if not has_other_active_promos:
                    logger.info(f"No other active promos for product {product.product_id}, resetting discount fields")
                    product.product_discountedPrice = None
                    product.is_discounted = False
                    product.has_promo = False
                    product.save(update_fields=['product_discountedPrice', 'is_discounted', 'has_promo'])
    except Exception as e:
        logger.error(f"Error removing promo {promo.promo_id} from products: {str(e)}")
        raise

def update_products_has_promo_on_m2m_change(promo, action, pk_set=None):
    """
    Updates has_promo field when products are added/removed from a promo.
    """
    try:
        with transaction.atomic():
            from ..models import Product
            
            if action == "post_clear":
                products = promo.product_id.all()
                logger.info(f"Clearing all products from promo {promo.promo_id}")
            else:
                products = Product.objects.filter(pk__in=pk_set) if pk_set else []
                logger.info(f"Updating {len(products)} products for promo {promo.promo_id} - Action: {action}")
            
            for product in products:
                update_product_has_promo_field(product)
    except Exception as e:
        logger.error(f"Error in M2M change for promo {promo.promo_id}: {str(e)}")
        raise