from django.urls import path
from . import views

urlpatterns = [
    path("store-products/", views.StorePostListCreate.as_view(), name="store-products"),
]