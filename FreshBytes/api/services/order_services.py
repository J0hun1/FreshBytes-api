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