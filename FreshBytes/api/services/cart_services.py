def generate_cart_id(last_cart):
    """Generate unique cart ID"""
    if last_cart:
        last_id = int(last_cart.cart_id[3:6])
        return f"cid{last_id + 1:03d}25"
    return "cid00125"

def generate_cart_item_id(last_cart_item):
    """Generate unique cart item ID"""
    if last_cart_item and last_cart_item.cart_item_id and len(last_cart_item.cart_item_id) >= 8:
        try:
            last_id = int(last_cart_item.cart_item_id[5:8])
            return f"citid{last_id + 1:03d}25"
        except (ValueError, IndexError):
            return "citid00125"
    return "citid00125"

def calculate_cart_item_total(product, quantity):
    """Calculate total price for cart item"""
    product_price = product.product_discountedPrice if product.is_discounted else product.product_price
    return product_price * quantity
