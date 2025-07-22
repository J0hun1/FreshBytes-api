from rest_framework import serializers
from ..models import Cart, CartItem

class CartItemSerializer(serializers.ModelSerializer):
    total_price = serializers.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        read_only=True
    )
    
    class Meta:
        model = CartItem
        fields = [
            'cart_id', 'cart_item_id', 'product', 'quantity', 
            'unit_price', 'total_price', 
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'unit_price', 'created_at', 'updated_at']

    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError("Quantity must be at least 1")
        return value

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.IntegerField(read_only=True)
    total_amount = serializers.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        read_only=True
    )

    class Meta:
        model = Cart
        fields = ['cart_id', 'user', 'items', 'total_items', 'total_amount', 'created_at', 'updated_at']
        read_only_fields = ['cart_id', 'created_at', 'updated_at']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Calculate totals
        data['total_items'] = sum(item.quantity for item in instance.items.all())
        data['total_amount'] = sum(item.total_price for item in instance.items.all())
        return data
