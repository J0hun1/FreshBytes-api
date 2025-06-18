from rest_framework import serializers
from .models import Product

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["product_id", "product_name", "product_price", "product_brief_description", "product_full_description", "product_discountedPrice", "product_sku", "product_unit", "product_status", "product_location", "user", "category", "quantity", "post_date", "harvest_date", "is_active", "seller", "discounted_amount", "is_discounted", "is_sale", "is_srp", "is_deleted", "brand", "top_rated", "sell_count", "offer_start_date", "offer_end_date", "promo_price", "created_at", "updated_at"]