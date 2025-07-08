from django.utils import timezone

def generate_review_id(last_review):
    """Generate unique review ID"""
    current_year = timezone.now().year % 100
    if last_review:
        last_id = int(last_review.review_id[3:6])
        return f"rid{last_id + 1:03d}{current_year:02d}"
    return f"rid001{current_year:02d}"

def update_product_review_stats(product):
    """Update product's review count and rating"""
    reviews = product.reviews_set.all()
    product.review_count = reviews.count()
    product.save(update_fields=['review_count'])

def update_seller_review_stats(seller):
    """Update seller's review statistics"""
    reviews = []
    for product in seller.product_set.all():
        reviews.extend(product.reviews_set.all())
    
    seller.total_reviews = len(reviews)
    if reviews:
        avg_rating = sum(review.review_rating for review in reviews) / len(reviews)
        seller.average_rating = round(avg_rating, 2)
    else:
        seller.average_rating = 0
    
    seller.save(update_fields=['total_reviews', 'average_rating']) 