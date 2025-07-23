from .product import ProductViewSet

from .user import (
    CustomTokenObtainPairView, RegisterView, LogoutView, UserViewSet, DeletedUserRetrieveDestroy,
    UserPermissionsView, UserRoleCheckView, AdminDashboardView
)
from .order import (
    OrderPostListCreate, OrderPostRetrieveUpdateDestroy, OrderCheckoutView, OrderStatusUpdateView, OrderArchiveView, OrderDetailView, OrderItemPostListCreate
)
from .seller import (
    AllSellersPostListCreate, AllSellersPostRetrieveUpdateDestroy, SellerProductsPostListCreate, SellerProductPostRetrieveUpdateDestroy, SellerCustomersView, SellerTransactionsView, SellerProductsBoughtByCustomerView
)
from .cart import CartViewSet
from .review import ReviewsPostListCreate, ReviewsPostRetrieveUpdateDestroy
from .promo import PromoPostListCreate, PromoPostRetrieveUpdateDestroy
from .payment import PaymentCreateView, PaymentDetailView
from .category import CategoryPostListCreate, CategoryPostRetrieveUpdateDestroy
from .subcategory import SubCategoryPostListCreate, SubCategoryPostRetrieveUpdateDestroy

# Add more imports here as you modularize other view domains
