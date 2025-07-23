from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'products', views.ProductViewSet, basename='product')
router.register(r'carts', views.CartViewSet, basename='cart')
router.register(r'users', views.UserViewSet, basename='user')
router.register(r'sellers', views.SellerViewSet, basename='seller')

urlpatterns = [
    # ========================================
    # AUTHENTICATION & AUTHORIZATION ENDPOINTS
    # ========================================
    # JWT token-based authentication
    path("auth/login/", views.CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),  # Login and get JWT tokens
    path("auth/login/refresh/", TokenRefreshView.as_view(), name="token_refresh"),  # Refresh expired JWT token
    path("auth/register/", views.RegisterView.as_view(), name="auth_register"),  # Register new user account
    path("auth/logout/", views.LogoutView.as_view(), name="auth_logout"),  # Logout and blacklist token
    
    # Permission and role checking endpoints
    path("auth/permissions/", views.UserPermissionsView.as_view(), name="user_permissions"),  # Get user's permissions and roles

    # ========================================
    # PRODUCT MANAGEMENT ENDPOINTS
    # ========================================
    # Product endpoints are now handled by the router

    # ========================================
    # CATEGORY MANAGEMENT ENDPOINTS
    # ========================================
    path("categories/", views.CategoryPostListCreate.as_view(), name="categories"),  # List all categories or create new category
    path("categories/<str:pk>/", views.CategoryPostRetrieveUpdateDestroy.as_view(), name="category-detail"),  # Get, update, or delete specific category

    # ========================================
    # SUBCATEGORY MANAGEMENT ENDPOINTS
    # ========================================
    path("subcategories/", views.SubCategoryPostListCreate.as_view(), name="subcategories"),  # List all subcategories or create new subcategory
    path("subcategories/<str:pk>/", views.SubCategoryPostRetrieveUpdateDestroy.as_view(), name="subcategory-detail"),  # Get, update, or delete specific subcategory

    # ========================================
    # USER MANAGEMENT ENDPOINTS
    # ========================================
    # User endpoints are now handled by the router

    # ========================================
    # SELLER MANAGEMENT ENDPOINTS
    # ========================================
    # Seller endpoints are now handled by the router

    # ========================================
    # REVIEW MANAGEMENT ENDPOINTS
    # ========================================
    path("reviews/", views.ReviewsPostListCreate.as_view(), name="reviews"),  # List all reviews or create new review
    path("reviews/<str:pk>/", views.ReviewsPostRetrieveUpdateDestroy.as_view(), name="review-detail"),  # Get, update, or delete specific review

    # ========================================
    # PROMO/DISCOUNT MANAGEMENT ENDPOINTS
    # ========================================
    path("promos/", views.PromoPostListCreate.as_view(), name="promos"),  # List all promos or create new promo (sellers/admins)
    path("promos/<str:pk>/", views.PromoPostRetrieveUpdateDestroy.as_view(), name="promo-detail"),  # Get, update, or delete specific promo

    # ========================================
    # SHOPPING CART ENDPOINTS
    # ========================================
    path('cart/', views.CartViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='cart'),  # Get user's cart or add item to cart
    path('cart/update-item/', views.CartViewSet.as_view({'post': 'update_item'}), name='cart-update-item'),  # Update quantity of item in cart
    path('cart/remove-item/', views.CartViewSet.as_view({'post': 'remove_item'}), name='cart-remove-item'),  # Remove specific item from cart
    path('cart/clear/', views.CartViewSet.as_view({'post': 'clear'}), name='cart-clear'),  # Clear all items from cart

    # ========================================
    # ORDER MANAGEMENT ENDPOINTS
    # ========================================
    path("orders/", views.OrderPostListCreate.as_view(), name="orders"),  # List all orders or create new order
    path("orders/checkout/", views.OrderCheckoutView.as_view(), name="order-checkout"),  # Create order from cart items
    path("orders/<uuid:id>/", views.OrderDetailView.as_view(), name="order-detail"),
    path("orders/<str:order_id>/status/", views.OrderStatusUpdateView.as_view(), name="order-status-update"),  # Update order status (seller/admin only, customer can cancel pending orders)
    path("orders/<uuid:order_id>/archive/", views.OrderArchiveView.as_view(), name="order-archive"),  # Archive or unarchive an order (admin or order owner)
    path("orders/<str:order_number>/", views.OrderDetailView.as_view(), name="order-detail"),  # Get, update, or delete specific order
    path("orders/number/<str:order_number>/", views.OrderDetailView.as_view(), name="order-detail-by-number"),

    # ========================================
    # ORDER ITEM MANAGEMENT ENDPOINTS
    # ========================================
    path("order-items/", views.OrderItemPostListCreate.as_view(), name="order-items"),  # List all order items or create new order item

    # ========================================
    # PAYMENT MANAGEMENT ENDPOINTS
    # ========================================
    path("payments/", views.PaymentCreateView.as_view(), name="payment-create"),  # Create new payment for order
    path("payments/<str:payment_id>/", views.PaymentDetailView.as_view(), name="payment-detail"),  # Get, update, or delete specific payment

    # ========================================
    # SELLER ANALYTICS & CUSTOMER TRACKING ENDPOINTS
    # ========================================
    # These endpoints are now handled by the SellerViewSet router registration

    # ========================================
    # ADMIN DASHBOARD ENDPOINT
    # ========================================
    path("admin/dashboard/", views.AdminDashboardView.as_view(), name="admin-dashboard"),
    *router.urls,
]