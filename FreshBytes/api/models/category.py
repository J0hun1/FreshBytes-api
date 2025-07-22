from django.db import models
from django.utils import timezone

class Category(models.Model):
    category_id = models.AutoField(primary_key=True)
    category_name = models.CharField(max_length=255, unique=True)
    category_description = models.CharField(max_length=255, default="")
    category_isActive = models.BooleanField(default=True)
    category_image = models.ImageField(upload_to='category_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Categories'

class SubCategory(models.Model):
    sub_category_id = models.CharField(primary_key=True, max_length=10, unique=True, editable=False)
    category_id = models.ForeignKey(Category, on_delete=models.CASCADE, null=True)
    sub_category_name = models.CharField(max_length=255, default="", unique=True)
    sub_category_description = models.CharField(max_length=255)
    sub_category_image = models.ImageField(upload_to='sub_category_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        from ..services.category_services import generate_subcategory_id, get_starting_counter
        if not self.sub_category_id:
            category_prefix = str(self.category_id.category_id) if self.category_id else "0"
            last_sub_category = SubCategory.objects.filter(
                category_id=self.category_id
            ).order_by('-created_at').first()
            starting_counter = get_starting_counter(category_prefix, last_sub_category)
            self.sub_category_id = generate_subcategory_id(category_prefix, starting_counter)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'SubCategory' 