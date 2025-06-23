from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.views import APIView
from .models import Product, Category, User, Seller, SubCategory, Reviews, Promo
from .serializers import ProductSerializer, CategorySerializer, UserSerializer, SellerSerializer, SubCategorySerializer, ReviewsSerializer, PromoSerializer
from rest_framework.response import Response

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

# New endpoints for managing products in promos
class PromoAddProducts(APIView):
    """Add products to a specific promo"""
    def post(self, request, promo_id):
        try:
            promo = Promo.objects.get(promo_id=promo_id)
            product_ids = request.data.get('product_ids', [])
            
            if not product_ids:
                return Response(
                    {'error': 'product_ids is required'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get the products
            products = Product.objects.filter(product_id__in=product_ids)
            
            if len(products) != len(product_ids):
                return Response(
                    {'error': 'Some product IDs are invalid'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Add products to the promo
            promo.product_id.add(*products)
            
            return Response({
                'message': f'Successfully added {len(products)} products to promo {promo_id}',
                'added_products': [p.product_id for p in products]
            }, status=status.HTTP_200_OK)
            
        except Promo.DoesNotExist:
            return Response(
                {'error': 'Promo not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'An error occurred: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class PromoRemoveProducts(APIView):
    """Remove products from a specific promo"""
    def post(self, request, promo_id):
        try:
            promo = Promo.objects.get(promo_id=promo_id)
            product_ids = request.data.get('product_ids', [])
            
            if not product_ids:
                return Response(
                    {'error': 'product_ids is required'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get the products
            products = Product.objects.filter(product_id__in=product_ids)
            
            if len(products) != len(product_ids):
                return Response(
                    {'error': 'Some product IDs are invalid'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Remove products from the promo
            promo.product_id.remove(*products)
            
            return Response({
                'message': f'Successfully removed {len(products)} products from promo {promo_id}',
                'removed_products': [p.product_id for p in products]
            }, status=status.HTTP_200_OK)
            
        except Promo.DoesNotExist:
            return Response(
                {'error': 'Promo not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'An error occurred: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class PromoGetProducts(APIView):
    """Get all products for a specific promo"""
    def get(self, request, promo_id):
        try:
            promo = Promo.objects.get(promo_id=promo_id)
            products = promo.product_id.all()
            
            product_data = ProductSerializer(products, many=True).data
            
            return Response({
                'promo_id': promo_id,
                'products': product_data,
                'total_products': len(product_data)
            }, status=status.HTTP_200_OK)
            
        except Promo.DoesNotExist:
            return Response(
                {'error': 'Promo not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'An error occurred: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class PromoClearProducts(APIView):
    """Remove all products from a specific promo"""
    def post(self, request, promo_id):
        try:
            promo = Promo.objects.get(promo_id=promo_id)
            
            # Get count before clearing
            product_count = promo.product_id.count()
            
            # Clear all products from the promo
            promo.product_id.clear()
            
            return Response({
                'message': f'Successfully removed all {product_count} products from promo {promo_id}'
            }, status=status.HTTP_200_OK)
            
        except Promo.DoesNotExist:
            return Response(
                {'error': 'Promo not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'An error occurred: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

#PROMO DETAILS
