from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from ..models import User

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
