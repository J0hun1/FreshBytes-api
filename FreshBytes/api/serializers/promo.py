from rest_framework import serializers
from ..models import Promo, Product

class PromoSerializer(serializers.ModelSerializer):
    product_id = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Product.objects.all(),
        required=False
    )

    class Meta:
        model = Promo
        fields = ["promo_id", "seller_id", "product_id", "promo_name", "promo_description", 
                 "discount_type", "discount_amount", "discount_percentage", 
                 "promo_start_date", "promo_end_date", "is_active", "created_at", "updated_at"]

    def validate(self, data):
        discount_type = data.get('discount_type')
        discount_percentage = data.get('discount_percentage')
        discount_amount = data.get('discount_amount')
        
        if discount_type == 'PERCENTAGE' and not discount_percentage:
            raise serializers.ValidationError("discount_percentage is required for percentage discount type.")
        if discount_type == 'FIXED' and not discount_amount:
            raise serializers.ValidationError("discount_amount is required for fixed discount type.")
        if data.get('promo_start_date') and data.get('promo_end_date'):
            if data.get('promo_start_date') >= data.get('promo_end_date'):
                raise serializers.ValidationError("promo_end_date must be after promo_start_date.")
        return data
