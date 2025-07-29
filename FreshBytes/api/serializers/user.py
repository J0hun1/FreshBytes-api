from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from ..models import User

class UserListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for user lists"""
    full_name = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()
    role_display = serializers.SerializerMethodField()
    created_date = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'user_id', 'user_name', 'full_name', 'user_email', 'role', 'role_display',
            'is_active', 'is_deleted', 'status_display', 'created_at', 'created_date'
        ]
        read_only_fields = ['user_id', 'created_at', 'full_name', 'status_display', 'role_display', 'created_date']

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()

    def get_status_display(self, obj):
        if obj.is_deleted:
            return "Deleted"
        elif not obj.is_active:
            return "Inactive"
        else:
            return "Active"

    def get_role_display(self, obj):
        role_mapping = {
            'admin': 'Administrator',
            'seller': 'Seller',
            'customer': 'Customer'
        }
        return role_mapping.get(obj.role, obj.role.title())

    def get_created_date(self, obj):
        return obj.created_at.strftime("%Y-%m-%d") if obj.created_at else None

class UserSerializer(serializers.ModelSerializer):
    # Password is optional for updates, required for user creation.
    password = serializers.CharField(write_only=True, required=False, allow_blank=False)
    full_name = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()
    role_display = serializers.SerializerMethodField()
    created_date = serializers.SerializerMethodField()
    updated_date = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['user_id', 'user_name', 'first_name', 'last_name', 'full_name', 'user_email', 
                 'password', 'user_phone', 'street', 'barangay', 'city', 'province', 'zip_code','role', 'role_display', 'created_at', 'updated_at', 'created_date', 'updated_date', 'is_active', 'is_deleted', 
                 'is_staff', 'is_superuser', 'terms_accepted', 'phone_verified', 'email_verified', 'status_display']
        read_only_fields = ['user_id', 'created_at', 'updated_at', 'full_name', 'status_display', 'role_display', 'created_date', 'updated_date']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()

    def get_status_display(self, obj):
        if obj.is_deleted:
            return "Deleted"
        elif not obj.is_active:
            return "Inactive"
        else:
            return "Active"

    def get_role_display(self, obj):
        role_mapping = {
            'admin': 'Administrator',
            'seller': 'Seller',
            'customer': 'Customer'
        }
        return role_mapping.get(obj.role, obj.role.title())

    def get_created_date(self, obj):
        return obj.created_at.strftime("%Y-%m-%d") if obj.created_at else None

    def get_updated_date(self, obj):
        return obj.updated_at.strftime("%Y-%m-%d") if obj.updated_at else None

    def validate(self, attrs):
        """Enforce that password is supplied on user creation, but optional on updates.
        Also require terms_accepted to be True and at least one of phone_verified or email_verified to be True on creation."""
        if self.instance is None:
            if not attrs.get('password'):
                raise serializers.ValidationError({"password": "This field is required."})
            if not attrs.get('terms_accepted', False):
                raise serializers.ValidationError({"terms_accepted": "You must accept the terms to create an account."})
            if not (attrs.get('phone_verified', False) or attrs.get('email_verified', False)):
                raise serializers.ValidationError({"verification": "Either phone or email must be verified to create an account."})
        return super().validate(attrs)

    def validate_role(self, value):
        request = self.context.get('request')
        # Only allow superusers to change the role
        if request and request.user and not request.user.is_superuser:
            # If updating and trying to change the role
            if self.instance and value != self.instance.role:
                raise serializers.ValidationError("You do not have permission to change roles.")
            # If creating and trying to set a role other than default
            if not self.instance and value != 'customer':
                raise serializers.ValidationError("You do not have permission to assign this role.")
        return value

    def create(self, validated_data):
        # Only allow 'customer' or 'seller' roles via public registration
        allowed_roles = ['customer', 'seller']
        requested_role = validated_data.get('role', 'customer')
        if requested_role not in allowed_roles:
            validated_data['role'] = 'customer'
        # `password` is guaranteed present here (see validate).
        validated_data['password'] = make_password(validated_data.get('password'))
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if 'password' in validated_data:
            validated_data['password'] = make_password(validated_data.get('password'))
        return super().update(instance, validated_data)
