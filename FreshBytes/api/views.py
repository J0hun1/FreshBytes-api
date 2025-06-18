from django.shortcuts import render
from rest_framework import generics, status
from .models import Product, Category
from .serializers import ProductSerializer, CategorySerializer
from rest_framework.response import Response
# Create your views here.


class ProductPostListCreate(generics.ListCreateAPIView):
    # getting Product objects that exist in the database
    queryset = Product.objects.all() 
    # serializing the data
    serializer_class = ProductSerializer

    #adds a delete endpoint to the list view
    def delete(self, request, *args, **kwargs):
        #deletes all products
        Product.objects.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class CategoryPostListCreate(generics.ListCreateAPIView):
     # getting Product objects that exist in the database
    queryset = Category.objects.all()
    # serializing the data
    serializer_class = CategorySerializer

    #adds a delete endpoint to the list view
    def delete(self, request, *args, **kwargs):
        #deletes all products
        Category.objects.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



#allows to access, update, and delete individual products
class ProductPostRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = "pk"

