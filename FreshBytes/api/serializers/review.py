from rest_framework import serializers
from ..models import Reviews

class ReviewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reviews
        fields = ["review_id", "product_id", "user_id", "review_rating", "review_comment", "review_date", "created_at", "updated_at"]
