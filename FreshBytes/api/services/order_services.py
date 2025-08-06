def generate_order_id(last_order):
    """Generate unique order ID"""
    if last_order:
        last_id = int(last_order.order_id[7:10])
        return f"oid{last_id + 1:03d}25"
    return "oid00125"

def generate_order_item_id(last_order_item):
    """Generate unique order item ID"""
    if last_order_item and last_order_item.order_item_id and len(last_order_item.order_item_id) >= 8:
        try:
            last_id = int(last_order_item.order_item_id[5:8])
            return f"oitid{last_id + 1:03d}25"
        except (ValueError, IndexError):
            return "oitid00125"
    return "oitid00125"

def calculate_order_item_total(product, quantity):
    """Calculate total price for order item"""
    product_price = product.product_discountedPrice if product.is_discounted else product.product_price
    return product_price * quantity 

from django.db import transaction
from ..models import Cart, CartItem, Order, OrderItem, Product, Payment
from ..utils.verification import check_user_verification

def validate_user_for_order(user):
    """Validate that user can place an order"""
    # Use the verification utility function
    check_user_verification(user, require_both=False)
    return True

def create_order_from_cart(user, cart_item_ids=None, payment_method=None):
    with transaction.atomic():
        # Validate user can place order
        validate_user_for_order(user)
        
        cart = Cart.objects.get(user=user)
        if cart_item_ids:
            items = cart.items.filter(cart_item_id__in=cart_item_ids)
        else:
            items = cart.items.all()
        if not items.exists():
            raise ValueError("No items in cart to order.")

        # Calculate order total
        order_total = sum(item.total_price for item in items)
        # TODO: Add discount, tax, shipping logic as needed

        # Create order
        order = Order.objects.create(
            user_id=user,
            order_total=order_total,
            # Add other fields as needed
        )

        # Create order items
        for item in items:
            OrderItem.objects.create(
                order_id=order,
                product_id=item.product,
                quantity=item.quantity,
                total_item_price=item.total_price,
                # Add discount_amount if needed
            )
            # Optionally: update product inventory
            item.product.quantity -= item.quantity
            item.product.save()

        # Create payment
        if not payment_method:
            raise ValueError("Payment method is required.")
        payment = Payment.objects.create(
            order_id=order,
            payment_method=payment_method,
            payment_status='PENDING',
            amount=order_total,
        )

        # Remove ordered items from cart
        items.delete()

        return order, payment 