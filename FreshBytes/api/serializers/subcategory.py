from rest_framework import serializers
from ..models import SubCategory

class SubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SubCategory
        fields = ["category_id", "sub_category_id", "sub_category_name", "sub_category_description", "sub_category_image", "created_at", "updated_at"] 