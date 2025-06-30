from django.urls import path
from . import views
from django.contrib import admin

urlpatterns = [
    path("admin/", admin.site.urls),

    # ALL DATA - Get all data from all models in one endpoint
    path("all-data/", views.AllDataView.as_view(), name="all-data"),

    #PRODUCTS 
        # list and create products
        path("products/", views.ProductPostListCreate.as_view(), name="products"),
        path("products", views.ProductPostListCreate.as_view(), name="products-no-slash"),
        # access, update, and delete individual products
        path("products/<str:pk>/", views.ProductPostRetrieveUpdateDestroy.as_view(), name="update-delete-product"),
        path("products/<str:pk>", views.ProductPostRetrieveUpdateDestroy.as_view(), name="update-delete-product-no-slash"),

    #CATEGORIES 
        # list and create categories
        path("categories/", views.CategoryPostListCreate.as_view(), name="categories"),
        path("categories/<str:pk>/", views.CategoryPostRetrieveUpdateDestroy.as_view(), name="update-delete-category"),
        path("categories/<str:pk>", views.CategoryPostRetrieveUpdateDestroy.as_view(), name="update-delete-category-no-slash"),

    #SUBCATEGORIES
        # list and create subcategories
        path("subcategories/", views.SubCategoryPostListCreate.as_view(), name="subcategories"),
        # access, update, and delete individual subcategories
        path("subcategories/<str:pk>/", views.SubCategoryPostRetrieveUpdateDestroy.as_view(), name="update-delete-subcategory"),

    #USERS 
        # list and create users
        path("users/", views.UserPostListCreate.as_view(), name="users"),
        # access, update, and delete individual users
        path("users/<str:pk>/", views.UserPostRetrieveUpdateDestroy.as_view(), name="update-delete-user"),

    #SELLERS 
        # list and create sellers
        path("sellers/", views.SellerPostListCreate.as_view(), name="sellers"),
        # access, update, and delete individual sellers
        path("sellers/<str:pk>/", views.SellerPostRetrieveUpdateDestroy.as_view(), name="update-delete-seller"),

    #REVIEWS
        # list and create reviews
        path("reviews/", views.ReviewsPostListCreate.as_view(), name="reviews"),
        # access, update, and delete individual reviews
        path("reviews/<str:pk>/", views.ReviewsPostRetrieveUpdateDestroy.as_view(), name="update-delete-review"),

    #PROMO
        # list and create promos
        path("promos/", views.PromoPostListCreate.as_view(), name="promos"),
        # access, update, and delete individual promos
        path("promos/<str:pk>/", views.PromoPostRetrieveUpdateDestroy.as_view(), name="update-delete-promo"),

    #CART
        path("carts/", views.CartPostListCreate.as_view(), name="carts"),
        path("cart-items/", views.CartItemPostListCreate.as_view(), name="cart-items"),

    #ORDERS 
        path("orders/", views.OrderPostListCreate.as_view(), name="orders"),
        path("orders/<str:pk>/", views.OrderPostRetrieveUpdateDestroy.as_view(), name="update-delete-order"),

    #ORDER ITEMS
        path("order-items/", views.OrderItemPostListCreate.as_view(), name="order-items"),  
]