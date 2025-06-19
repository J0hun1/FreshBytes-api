from rest_framework import serializers
from .models import Product
from .models import Category
from .models import User
from .models import Seller

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["product_id", "user_id", "seller_id", "product_name", "product_price", "product_brief_description", "product_full_description", "product_discountedPrice", "product_sku", "product_status", "product_location", "category_id", "quantity", "post_date", "harvest_date", "is_active", "discounted_amount", "is_discounted", "is_srp", "is_deleted", "top_rated", "sell_count", "offer_start_date", "offer_end_date", "created_at", "updated_at"]

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["category_id", "category_name", "category_isActive", "category_image", "created_at", "updated_at"]

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["user_id", "user_name", "first_name", "last_name", "user_email", "user_password", "user_phone", "user_address", "created_at", "updated_at", "is_active", "is_deleted", "is_admin"]

class SellerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seller
        fields = ["seller_id", "user_id", "business_name", "business_email", "business_phone", "business_address", "total_earnings", "total_products", "total_orders", "total_reviews", "average_rating", "total_followers", "total_products_sold", "created_at", "updated_at", "is_active", "is_deleted"]
