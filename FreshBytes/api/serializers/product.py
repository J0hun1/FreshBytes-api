from rest_framework import serializers
from ..models import Product

class ProductSerializer(serializers.ModelSerializer):
    category_id = serializers.SerializerMethodField(read_only=True)
    product_status = serializers.ChoiceField(
        choices=[
            ('ROTTEN', 'Rotten'),
            ('SLIGHTLY_WITHERED', 'Slightly Withered'),
            ('FRESH', 'Fresh')
        ],
        default='FRESH'
    )
    product_sku = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=50)

    class Meta:
        model = Product
        fields = [
            "product_id", "user_id", "seller_id", "product_name", "product_price", 
            "product_brief_description", "product_full_description", "product_discountedPrice", 
            "product_sku", "product_status", "product_location", "sub_category_id", 
            "category_id", "quantity", "post_date", "harvest_date", "is_active", 
            "review_count", "top_rated", "discounted_amount", "is_discounted", 
            "is_srp", "is_deleted", "sell_count", "created_at", "updated_at", "has_promo"
        ]

    def get_category_id(self, obj):
        return obj.category_id.category_id if obj.category_id else None

    def validate_product_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Product price must be greater than 0.")
        return value

    def validate_product_sku(self, value):
        if not value:
            return value
        view = self.context.get('view')
        seller_id = None
        if view:
            seller_id = view.kwargs.get('seller_id')
        # During update, instance may exist
        instance = getattr(self, 'instance', None)
        qs = Product.objects.all()
        if seller_id:
            qs = qs.filter(seller_id=seller_id)
        if instance:
            qs = qs.exclude(pk=instance.pk)
        if qs.filter(product_sku=value).exists():
            raise serializers.ValidationError("SKU already exists for this seller.")
        return value
