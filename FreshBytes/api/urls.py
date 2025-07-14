from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    # Authentication endpoints
    path("auth/login/", views.CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/login/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("auth/register/", views.RegisterView.as_view(), name="auth_register"),
    path("auth/logout/", views.LogoutView.as_view(), name="auth_logout"),
    path("auth/test/", views.TestAuthView.as_view(), name="test_auth"),

    # PRODUCTS 
    path("products/", views.ProductPostListCreate.as_view(), name="products"),
    path("products/<str:pk>/", views.ProductPostRetrieveUpdateDestroy.as_view(), name="product-detail"),

    # CATEGORIES 
    path("categories/", views.CategoryPostListCreate.as_view(), name="categories"),
    path("categories/<str:pk>/", views.CategoryPostRetrieveUpdateDestroy.as_view(), name="category-detail"),

    # SUBCATEGORIES
    path("subcategories/", views.SubCategoryPostListCreate.as_view(), name="subcategories"),
    path("subcategories/<str:pk>/", views.SubCategoryPostRetrieveUpdateDestroy.as_view(), name="subcategory-detail"),

    # USERS 
    # Deleted users endpoints must come first to avoid catching 'deleted' as pk
    path("users/deleted/", views.DeletedUsersListDelete.as_view(), name="deleted-users"),
    path("users/deleted/<uuid:pk>/", views.DeletedUserRetrieveDestroy.as_view(), name="deleted-user-detail"),
    # Regular users endpoints
    path("users/", views.UserPostListCreate.as_view(), name="users"),
    path("users/<uuid:pk>/", views.UserPostRetrieveUpdateDestroy.as_view(), name="user-detail"),
    path("users/restore/<uuid:pk>/", views.RestoreUser.as_view(), name="user-restore"),

    # SELLERS 
    path("sellers/", views.AllSellersPostListCreate.as_view(), name="seller-list-create"),
    path("sellers/<uuid:pk>/", views.AllSellersPostRetrieveUpdateDestroy.as_view(), name="seller-detail"),
    path("sellers/<uuid:seller_id>/products/", views.SellerProductsPostListCreate.as_view(), name="seller-products"),
    path("sellers/<uuid:seller_id>/products/<uuid:product_id>/", views.SellerProductPostRetrieveUpdateDestroy.as_view(), name="seller-product-detail"),

    path("sellers/<uuid:seller_id>/<uuid:product_id>/", views.SellerProductPostRetrieveUpdateDestroy.as_view(), name="seller-product-delete"),

    # REVIEWS
    path("reviews/", views.ReviewsPostListCreate.as_view(), name="reviews"),
    path("reviews/<str:pk>/", views.ReviewsPostRetrieveUpdateDestroy.as_view(), name="review-detail"),

    # PROMO
    path("promos/", views.PromoPostListCreate.as_view(), name="promos"),
    path("promos/<str:pk>/", views.PromoPostRetrieveUpdateDestroy.as_view(), name="promo-detail"),

    # CART
    # path("carts/", views.CartPostListCreate.as_view(), name="carts"),
    path('cart/', views.CartViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='cart'),
    path('cart/update-item/', views.CartViewSet.as_view({'post': 'update_item'}), name='cart-update-item'),
    path('cart/remove-item/', views.CartViewSet.as_view({'post': 'remove_item'}), name='cart-remove-item'),
    path('cart/clear/', views.CartViewSet.as_view({'post': 'clear'}), name='cart-clear'),

    # ORDERS 
    path("orders/", views.OrderPostListCreate.as_view(), name="orders"),
    path("orders/<str:pk>/", views.OrderPostRetrieveUpdateDestroy.as_view(), name="order-detail"),

    # ORDER ITEMS
    path("order-items/", views.OrderItemPostListCreate.as_view(), name="order-items"),
]