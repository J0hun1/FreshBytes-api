from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.views import APIView
from .models import Product, Category, User, Seller, SubCategory, Reviews, Promo, Cart, CartItem
from .serializers import ProductSerializer, CategorySerializer, UserSerializer, SellerSerializer, SubCategorySerializer, ReviewsSerializer, PromoSerializer
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

# Create your views here.

# ALL DATA VIEW - Returns all data from all models
class AllDataView(APIView):
    def get(self, request):
        """Get all data from all models in a single response"""
        try:
            # Get all data from each model
            products = Product.objects.all()
            categories = Category.objects.all()
            users = User.objects.all()
            sellers = Seller.objects.all()
            subcategories = SubCategory.objects.all()
            reviews = Reviews.objects.all()
            
            # Serialize the data
            product_data = ProductSerializer(products, many=True).data
            category_data = CategorySerializer(categories, many=True).data
            user_data = UserSerializer(users, many=True).data
            seller_data = SellerSerializer(sellers, many=True).data
            subcategory_data = SubCategorySerializer(subcategories, many=True).data
            review_data = ReviewsSerializer(reviews, many=True).data
            
            # Combine all data into a single response
            all_data = {
                'products': product_data,
                'categories': category_data,
                'users': user_data,
                'sellers': seller_data,
                'subcategories': subcategory_data,
                'reviews': review_data,
                'summary': {
                    'total_products': products.count(),
                    'total_categories': categories.count(),
                    'total_users': users.count(),
                    'total_sellers': sellers.count(),
                    'total_subcategories': subcategories.count(),
                    'total_reviews': reviews.count(),
                }
            }
            
            return Response(all_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': f'An error occurred while fetching data: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

#PRODUCTS
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
    

#allows to access, update, and delete individual products
class ProductPostRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = "pk"

#CATEGORIES
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

class CategoryPostRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = "pk"

# SUBCATEGORIES
class SubCategoryPostListCreate(generics.ListCreateAPIView):
    queryset = SubCategory.objects.all()
    serializer_class = SubCategorySerializer

    def delete(self, request, *args, **kwargs):
        #deletes all subcategories
        SubCategory.objects.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class SubCategoryPostRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = SubCategory.objects.all()
    serializer_class = SubCategorySerializer
    lookup_field = "pk"

#USERS
class UserPostListCreate(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def delete(self, request, *args, **kwargs):
        #deletes all users
        User.objects.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

#allows to access, update, and delete individual users
class UserPostRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = "pk"


#SELLERS
class SellerPostListCreate(generics.ListCreateAPIView):
    queryset = Seller.objects.all()
    serializer_class = SellerSerializer
    def delete(self, request, *args, **kwargs):
        #deletes all sellers
        Seller.objects.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
#allows to access, update, and delete individual sellers
class SellerPostRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Seller.objects.all()
    serializer_class = SellerSerializer
    lookup_field = "pk"


#REVIEWS
class ReviewsPostListCreate(generics.ListCreateAPIView):
    queryset = Reviews.objects.all()
    serializer_class = ReviewsSerializer

    def delete(self, request, *args, **kwargs):
        #deletes all reviews
        Reviews.objects.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class ReviewsPostRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Reviews.objects.all()
    serializer_class = ReviewsSerializer
    lookup_field = "pk"

#PROMO
class PromoPostListCreate(generics.ListCreateAPIView):
    queryset = Promo.objects.all()
    serializer_class = PromoSerializer

    def delete(self, request, *args, **kwargs):
        #deletes all promos
        Promo.objects.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class PromoPostRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Promo.objects.all()
    serializer_class = PromoSerializer
    lookup_field = "pk"


#CART