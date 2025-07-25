from rest_framework import serializers
from ..models import Seller

class SellerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seller
        fields = ["seller_id", "user_id", "business_name", 'street', 'barangay', 'city', 'province', 'zip_code', "business_phone", "total_earnings", "total_products", "total_orders", "total_reviews", "average_rating", "total_followers", "total_likes", "total_products_sold", "is_active", "is_deleted", "is_verified", "terms_accepted", "created_at", "updated_at", ]
