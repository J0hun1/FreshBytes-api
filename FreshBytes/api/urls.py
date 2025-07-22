from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenRefreshView

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
    path("auth/check-roles/", views.UserRoleCheckView.as_view(), name="check_roles"),  # Check if user has specific roles

    # ========================================
    # PRODUCT MANAGEMENT ENDPOINTS
    # ========================================
    path("products/", views.ProductPostListCreate.as_view(), name="products"),  # List all products or create new product
    path("products/<str:pk>/", views.ProductPostRetrieveUpdateDestroy.as_view(), name="product-detail"),  # Get, update, or delete specific product
    path("products/<uuid:product_id>/soft-delete/", views.ProductSoftDeleteView.as_view(), name="product-soft-delete"),  # Soft-delete a product (set is_deleted=True)
    path("products/<uuid:product_id>/restore/", views.ProductRestoreView.as_view(), name="product-restore"),  # Restore a soft-deleted product (set is_deleted=False)
    path("products/deleted/", views.DeletedProductListView.as_view(), name="deleted-product-list"),  # List all soft-deleted products

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
    # Deleted users endpoints must come first to avoid catching 'deleted' as pk
    path("users/deleted/", views.DeletedUsersListDelete.as_view(), name="deleted-users"),  # List all soft-deleted users
    path("users/deleted/<uuid:pk>/", views.DeletedUserRetrieveDestroy.as_view(), name="deleted-user-detail"),  # Get or permanently delete specific deleted user
    # Regular users endpoints
    path("users/", views.UserPostListCreate.as_view(), name="users"),  # List all users or create new user (admin only)
    path("users/<uuid:pk>/", views.UserPostRetrieveUpdateDestroy.as_view(), name="user-detail"),  # Get, update, or delete specific user
    path("users/restore/<uuid:pk>/", views.RestoreUser.as_view(), name="user-restore"),  # Restore soft-deleted user (admin only)
    path("users/disable/<uuid:pk>/", views.DisableUser.as_view(), name="user-disable"),  # Disable user account (admin only)
    path("users/enable/<uuid:pk>/", views.EnableUser.as_view(), name="user-enable"),  # Enable disabled user account (admin only)

    # ========================================
    # SELLER MANAGEMENT ENDPOINTS
    # ========================================
    path("sellers/", views.AllSellersPostListCreate.as_view(), name="seller-list-create"),  # List all sellers or create seller profile
    path("sellers/<uuid:pk>/", views.AllSellersPostRetrieveUpdateDestroy.as_view(), name="seller-detail"),  # Get, update, or delete specific seller profile
    path("sellers/<uuid:seller_id>/products/", views.SellerProductsPostListCreate.as_view(), name="seller-products"),  # List products by specific seller or add product to seller
    path("sellers/<uuid:seller_id>/products/<uuid:product_id>/", views.SellerProductPostRetrieveUpdateDestroy.as_view(), name="seller-product-detail"),  # Get, update, or delete specific product for seller
    path("sellers/<uuid:seller_id>/<uuid:product_id>/", views.SellerProductPostRetrieveUpdateDestroy.as_view(), name="seller-product-delete"),  # Alternative route for seller product operations

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
    path('sellers/<uuid:seller_id>/customers/', views.SellerCustomersView.as_view(), name='seller-customers'),  # Get list of customers who bought from specific seller
    path('sellers/<uuid:seller_id>/transactions/', views.SellerTransactionsView.as_view(), name='seller-transactions'),  # Get all transactions/orders for specific seller
    path('sellers/<uuid:seller_id>/customers/<uuid:customer_id>/products/', views.SellerProductsBoughtByCustomerView.as_view(), name='seller-products-by-customer'),  # Get products bought by specific customer from specific seller
]