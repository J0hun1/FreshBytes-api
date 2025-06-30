from rest_framework import serializers
from .models import Product
from .models import Category
from .models import User
from .models import Seller
from .models import SubCategory
from .models import Reviews
from .models import Promo
from .models import Cart
from .models import CartItem
from .models import Order
from .models import OrderItem

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["product_id", "user_id", "seller_id", "product_name", "product_price", "product_brief_description", "product_full_description", "product_discountedPrice", "product_sku", "product_status", "product_location", "category_id", "sub_category_id", "quantity", "post_date", "harvest_date", "is_active", "review_count", "top_rated", "discounted_amount", "is_discounted", "is_srp", "is_deleted", "sell_count", "offer_start_date", "offer_end_date", "created_at", "updated_at", "has_promo"]

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["category_id", "category_name", "category_description", "category_isActive", "category_image", "created_at", "updated_at"]

class SubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SubCategory
        fields = ["category_id", "sub_category_id", "sub_category_name", "sub_category_description", "sub_category_image", "created_at", "updated_at"]


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["user_id", "user_name", "first_name", "last_name", "user_email", "user_password", "user_phone", "user_address", "created_at", "updated_at", "is_active", "is_deleted", "is_admin"]

class SellerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seller
        fields = ["seller_id", "user_id", "business_name", "business_email", "business_phone", "business_address", "total_earnings", "total_products", "total_orders", "total_reviews", "average_rating", "total_followers", "total_products_sold", "created_at", "updated_at", "is_active", "is_deleted"]

class ReviewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reviews
        fields = ["review_id", "product_id", "user_id", "review_rating", "review_comment", "review_date", "created_at", "updated_at"]

class PromoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Promo
        fields = ["promo_id", "seller_id", "product_id", "promo_name", "promo_description", "discount_type", "discount_amount", "discount_percentage", "promo_start_date", "promo_end_date", "is_active", "created_at", "updated_at"]


class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ["cart_id", "user_id", "created_at", "updated_at"]

class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ["cart_item_id", "cart_id", "product_id", "quantity", "total_item_price", "discount_amount", "discount_percentage", "created_at", "updated_at"]

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ["order_id", "user_id", "order_date", "order_total", "discount_amount", "discount_percentage", "order_status", "created_at", "updated_at"]

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ["order_item_id", "order_id", "product_id", "quantity", "total_item_price", "discount_amount", "created_at", "updated_at"]