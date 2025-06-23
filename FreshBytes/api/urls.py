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
        # access, update, and delete individual products
        path("products/<str:pk>/", views.ProductPostRetrieveUpdateDestroy.as_view(), name="update-delete-product"),

    #CATEGORIES 
        # list and create categories
        path("categories/", views.CategoryPostListCreate.as_view(), name="categories"),


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
        # manage products in promos
        path("promos/<str:promo_id>/add-products/", views.PromoAddProducts.as_view(), name="promo-add-products"),
        path("promos/<str:promo_id>/remove-products/", views.PromoRemoveProducts.as_view(), name="promo-remove-products"),
        path("promos/<str:promo_id>/products/", views.PromoGetProducts.as_view(), name="promo-get-products"),
        path("promos/<str:promo_id>/clear-products/", views.PromoClearProducts.as_view(), name="promo-clear-products"),


    #PROMO DETAILS
]