from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from ..models import User

class UserSerializer(serializers.ModelSerializer):
    # Password is optional for updates, required for user creation.
    password = serializers.CharField(write_only=True, required=False, allow_blank=False)

    class Meta:
        model = User
        fields = ['user_id', 'user_name', 'first_name', 'last_name', 'user_email', 
                 'password', 'user_phone', 'street', 'barangay', 'city', 'province', 'zip_code','role', 'created_at', 'updated_at', 'is_active', 'is_deleted', 
                 'is_staff', 'is_superuser', 'terms_accepted', 'phone_verified', 'email_verified']
        read_only_fields = ['user_id', 'created_at', 'updated_at']
        extra_kwargs = {
            'password': {'write_only': True}
        }

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
