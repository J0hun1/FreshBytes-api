from rest_framework import serializers
from ..models import Category

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["category_id", "category_name", "category_description", "category_isActive", "category_image", "created_at", "updated_at"] 