from django.shortcuts import get_object_or_404
from django.db import transaction
from django.core.exceptions import ValidationError
from ..models import Cart, CartItem, Product
from ..utils.verification import check_user_verification

def validate_user_for_cart(user):
    """Validate that user can use cart functionality"""
    # Use the verification utility function
    check_user_verification(user, require_both=False)
    return True

def get_or_create_cart(user):
    """Get existing cart or create a new one for the user."""
    validate_user_for_cart(user)
    cart, created = Cart.objects.get_or_create(user=user)
    return cart

def add_to_cart(user, product_id, quantity=1):
    """Add a product to user's cart. Update quantity if product already exists."""
    with transaction.atomic():
        validate_user_for_cart(user)
        cart = get_or_create_cart(user)
        product = get_object_or_404(Product, pk=product_id)
        
        # Check if product is available
        if not product.is_active or product.is_deleted:
            raise ValueError("This product is not available.")
        
        # Check stock availability
        if product.quantity < quantity:
            raise ValueError(f"Insufficient stock. Only {product.quantity} items available.")
        
        # Get or create cart item
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )
        
        if not created:
            # Update quantity if item already exists
            new_quantity = cart_item.quantity + quantity
            if product.quantity < new_quantity:
                raise ValueError(f"Insufficient stock. Only {product.quantity} items available.")
            cart_item.quantity = new_quantity
            cart_item.save()
            
        return cart_item

def update_cart_item(user, product_id, quantity):
    """Update quantity of a cart item."""
    with transaction.atomic():
        validate_user_for_cart(user)
        cart = get_object_or_404(Cart, user=user)
        cart_item = get_object_or_404(CartItem, cart=cart, product_id=product_id)
        
        if quantity < 1:
            cart_item.delete()
            return None
        
        # Check stock availability
        product = cart_item.product
        if product.quantity < quantity:
            raise ValueError(f"Insufficient stock. Only {product.quantity} items available.")
            
        cart_item.quantity = quantity
        cart_item.save()
        return cart_item

def remove_from_cart(user, product_id):
    """Remove a product from user's cart."""
    validate_user_for_cart(user)
    cart = get_object_or_404(Cart, user=user)
    CartItem.objects.filter(cart=cart, product_id=product_id).delete()

def clear_cart(user):
    """Remove all items from user's cart."""
    validate_user_for_cart(user)
    cart = get_object_or_404(Cart, user=user)
    cart.items.all().delete()

def get_cart_summary(user):
    """Get cart with total items and amount."""
    validate_user_for_cart(user)
    cart = get_object_or_404(Cart, user=user)
    return {
        'id': cart.id,
        'total_items': sum(item.quantity for item in cart.items.all()),
        'total_amount': sum(item.total_price for item in cart.items.all()),
        'items': cart.items.all()
    }
