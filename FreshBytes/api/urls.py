from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'products', views.ProductViewSet, basename='product')
router.register(r'carts', views.CartViewSet, basename='cart')
router.register(r'users', views.UserViewSet, basename='user')
router.register(r'sellers', views.SellerViewSet, basename='seller')
router.register(r'orders', views.OrderViewSet, basename='order')
router.register(r'order-items', views.OrderItemViewSet, basename='order-item')
router.register(r'reviews', views.ReviewsViewSet, basename='review')
router.register(r'promos', views.PromoViewSet, basename='promo')
router.register(r'categories', views.CategoryViewSet, basename='category')
router.register(r'subcategories', views.SubCategoryViewSet, basename='subcategory')
router.register(r'payments', views.PaymentViewSet, basename='payment')

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

    # ========================
    # ADMIN DASHBOARD ENDPOINT
    # ========================
    path("admin/dashboard/", views.AdminDashboardView.as_view(), name="admin-dashboard"),
    *router.urls,
]