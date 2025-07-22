from rest_framework import serializers
from .models import Product, Category, User, Seller, SubCategory, Reviews, Promo, Cart, CartItem, Order, OrderItem, Payment
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.hashers import make_password

User = get_user_model()

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims
        token['user_email'] = user.user_email
        token['role'] = user.role  # Keep for backward compatibility
        token['user_name'] = user.user_name
        
        # Add group information for new permission system
        token['groups'] = [group.name for group in user.groups.all()]
        token['primary_role'] = user.get_primary_role()
        
        # Add some key permissions for quick frontend checks
        token['permissions'] = {
            'can_manage_products': user.has_perm('api.add_product') and user.has_perm('api.change_product'),
            'can_approve_products': user.has_perm('api.can_approve_products'),
            'can_view_seller_stats': user.has_perm('api.can_view_seller_stats'),
            'can_manage_users': user.has_perm('api.can_manage_sellers'),
            'is_admin': user.is_admin(),
            'is_seller': user.is_seller(),
            'is_customer': user.is_customer()
        }
        
        return token

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
    

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["category_id", "category_name", "category_description", "category_isActive", "category_image", "created_at", "updated_at"]

class SubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SubCategory
        fields = ["category_id", "sub_category_id", "sub_category_name", "sub_category_description", "sub_category_image", "created_at", "updated_at"]


class UserSerializer(serializers.ModelSerializer):
    # Password is optional for updates, required for user creation.
    password = serializers.CharField(write_only=True, required=False, allow_blank=False)

    class Meta:
        model = User
        fields = ['user_id', 'user_name', 'first_name', 'last_name', 'user_email', 
                 'password', 'user_phone', 'street', 'barangay', 'city', 'province', 'zip_code','role', 'created_at', 'updated_at', 'is_active', 'is_deleted', 'is_superuser', ]
        read_only_fields = ['user_id', 'created_at', 'updated_at']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate(self, attrs):
        """Enforce that password is supplied on user creation, but optional on updates."""
        if self.instance is None and not attrs.get('password'):
            raise serializers.ValidationError({"password": "This field is required."})
        return super().validate(attrs)

    def create(self, validated_data):
        # `password` is guaranteed present here (see validate).
        validated_data['password'] = make_password(validated_data.get('password'))
        if validated_data.get('role') == 'admin':
            validated_data['is_staff'] = True
            validated_data['is_superuser'] = True
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if 'password' in validated_data:
            validated_data['password'] = make_password(validated_data.get('password'))
        return super().update(instance, validated_data)

class SellerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seller
        fields = ["seller_id", "user_id", "business_name", 'street', 'barangay', 'city', 'province', 'zip_code', "business_phone", "total_earnings", "total_products", "total_orders", "total_reviews", "average_rating", "total_followers", "total_likes", "total_products_sold", "created_at", "updated_at", "is_active", "is_deleted"]

class ReviewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reviews
        fields = ["review_id", "product_id", "user_id", "review_rating", "review_comment", "review_date", "created_at", "updated_at"]

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


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'
        read_only_fields = ['payment_id', 'created_at', 'updated_at', 'payment_date']