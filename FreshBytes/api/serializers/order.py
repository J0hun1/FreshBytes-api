from rest_framework import serializers
from ..models import Order, OrderItem

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            "order_id", "user_id", "order_date", "order_total", "order_status", "created_at", "updated_at", "is_archived","order_number"
        ]

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = [
            "order_item_id", "order_id", "product_id", "quantity", "total_item_price", "created_at", "updated_at"
        ]
