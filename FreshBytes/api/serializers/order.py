from rest_framework import serializers
from ..models import Order, OrderItem

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            "order_id", "user_id", "order_date", "order_total", "order_status", "created_at", "updated_at", "is_archived","order_number"
        ]

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product_id.product_name', read_only=True)
    product_price = serializers.CharField(source='product_id.product_price', read_only=True)
    first_name = serializers.CharField(source='order_id.user_id.first_name', read_only=True)
    last_name = serializers.CharField(source='order_id.user_id.last_name', read_only=True)
    business_name = serializers.CharField(source='product_id.seller_id.business_name', read_only=True)
    order_status = serializers.CharField(source='order_id.order_status', read_only=True)

    
    class Meta:
        model = OrderItem
        fields = [
            "order_item_id", "order_id", "product_id", "product_name", "product_price", "first_name", "last_name", "business_name", "order_status", "quantity", "total_item_price", "created_at", "updated_at"
        ]
