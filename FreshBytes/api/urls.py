from django.urls import path
from . import views

urlpatterns = [
    #PRODUCTS 
        # list and create products
        path("products/", views.ProductPostListCreate.as_view(), name="products"),
        # access, update, and delete individual products
        path("products/<str:pk>/", views.ProductPostRetrieveUpdateDestroy.as_view(), name="update-delete-product"),

        # list and create categories
        path("categories/", views.CategoryPostListCreate.as_view(), name="categories"),

    #CATEGORIES 
        # list and create categories
        path("categories/", views.CategoryPostListCreate.as_view(), name="categories"),

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






]