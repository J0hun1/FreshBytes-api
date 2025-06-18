from django.shortcuts import render
from rest_framework import generics
from .models import Product
from .serializers import ProductSerializer
# Create your views here.

class StorePostListCreate(generics.ListCreateAPIView):
    # getting Product objects that exist in the database
    queryset = Product.objects.all() 
    # serializing the data
    serializer_class = ProductSerializer