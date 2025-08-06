from django.urls import path
from . import views
from .views import health
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

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
    
    # Comprehensive health check for monitoring
    path("health/", health.health_check, name="health_check"),
    # Simple health check for load balancers
    path("health/simple/", health.simple_health_check, name="simple_health_check"),
    
    # JWT token-based authentication
    path("auth/login/", views.CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),  
    # Refresh expired JWT token
    path("auth/login/refresh/", TokenRefreshView.as_view(), name="token_refresh"),  
    # Register new user account
    path("auth/register/", views.RegisterView.as_view(), name="auth_register"),  
    # Logout and blacklist token
    path("auth/logout/", views.LogoutView.as_view(), name="auth_logout"),  
    
    # Permission and role checking endpoints
    path("auth/permissions/", views.UserPermissionsView.as_view(), name="user_permissions"),  
    # User verification status endpoint
    path("auth/verification-status/", views.UserVerificationStatusView.as_view(), name="user_verification_status"),  

    # Admin dashboard
    path("admin/dashboard/", views.AdminDashboardView.as_view(), name="admin-dashboard"),
    *router.urls,


    # Store dashboard
    path("store/dashboard/", views.StoreDashboardView.as_view(), name="store-dashboard"),
    *router.urls,

    # Swagger documentation endpoints
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]