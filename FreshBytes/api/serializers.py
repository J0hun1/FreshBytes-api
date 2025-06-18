from rest_framework import serializers
from .models import Product
from .models import Category

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["product_id", "product_name", "product_price", "product_brief_description", "product_full_description", "product_discountedPrice", "product_sku", "product_status", "product_location", "category_id", "quantity", "post_date", "harvest_date", "is_active", "discounted_amount", "is_discounted", "is_sale", "is_srp", "is_deleted", "top_rated", "sell_count", "offer_start_date", "offer_end_date", "promo_price", "created_at", "updated_at"]

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["category_id", "category_name", "category_isActive", "category_image", "created_at", "updated_at"]