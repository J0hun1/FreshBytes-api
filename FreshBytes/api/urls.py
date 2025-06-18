from django.urls import path
from . import views

urlpatterns = [
    # list and create products
    path("products/", views.ProductPostListCreate.as_view(), name="products"),

    # list and create categories
    path("categories/", views.CategoryPostListCreate.as_view(), name="categories"),

    # access, update, and delete individual products
    path("products/<int:pk>/", views.ProductPostRetrieveUpdateDestroy.as_view(), name="update-delete-product"),

]