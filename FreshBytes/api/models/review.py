from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from .user import User
from .product import Product

class Reviews(models.Model):
    review_id = models.CharField(primary_key=True, max_length=10, unique=True, editable=False)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True, db_column='user_id')
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    review_rating = models.IntegerField(default=0, validators=[MinValueValidator(1), MaxValueValidator(5)])
    review_comment = models.CharField(max_length=255)
    review_date = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        from ..services.review_services import generate_review_id, update_product_review_stats, update_seller_review_stats
        if not self.review_id:
            last_review = Reviews.objects.order_by('-created_at').first()
            self.review_id = generate_review_id(last_review)
        super().save(*args, **kwargs)
        # Update related statistics
        if self.product_id:
            update_product_review_stats(self.product_id)
            if self.product_id.seller_id:
                update_seller_review_stats(self.product_id.seller_id)

    class Meta:
        db_table = 'Reviews'
