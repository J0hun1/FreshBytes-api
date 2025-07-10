from django.shortcuts import render
from rest_framework import generics, status, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, BasePermission, AllowAny
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Product, Category, User, Seller, SubCategory, Reviews, Promo, Cart, CartItem, Order, OrderItem
from .serializers import (
    ProductSerializer, CategorySerializer, UserSerializer, SellerSerializer, 
    SubCategorySerializer, ReviewsSerializer, PromoSerializer, CartSerializer, 
    CartItemSerializer, OrderSerializer, OrderItemSerializer, CustomTokenObtainPairSerializer
)
from rest_framework import serializers
from .services.cart_services import get_or_create_cart, add_to_cart, update_cart_item, remove_from_cart, clear_cart
from django.core.exceptions import ValidationError
from rest_framework.decorators import action

# Custom permission classes
class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.role == 'admin'

class IsSeller(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.role == 'seller'

class IsCustomer(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.role == 'customer'

# New permission: allow either sellers or admins
class IsSellerOrAdmin(BasePermission):
    """Permission that allows access to users with role 'seller' OR 'admin'."""
    def has_permission(self, request, view):
        return request.user and request.user.role in ['seller', 'admin']

# Authentication Views
class CustomTokenObtainPairView(TokenObtainPairView):
    permission_classes = [AllowAny]
    serializer_class = CustomTokenObtainPairSerializer

class RegisterView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    queryset = User.objects.all()
    serializer_class = UserSerializer

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Successfully logged out."}, status=status.HTTP_200_OK)
        except Exception:
            return Response({"error": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)


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
    permission_classes = [IsAuthenticated, IsAdmin]

    def delete(self, request, *args, **kwargs):
        if not (request.user.role == 'admin'):
            return Response({"error": "Only admins can perform this action."}, 
                          status=status.HTTP_403_FORBIDDEN)
        User.objects.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

#allows to access, update, and delete individual users
class UserPostRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "pk"

    def get_permissions(self):
        if self.request.method in ['DELETE']:
            return [IsAuthenticated(), IsAdmin()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return User.objects.all()
        return User.objects.filter(user_id=user.user_id)
        
    def perform_destroy(self, instance):
        """Soft delete the user instead of hard delete"""
        instance.is_deleted = True
        instance.is_active = False
        instance.save()


#SELLERS
class AllSellersPostListCreate(generics.ListCreateAPIView):
    queryset = Seller.objects.all()
    serializer_class = SellerSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        """Create a seller profile.

        Behaviour:
        • Customers can create *their own* seller profile – their role is promoted to "seller".
        • Admins can create a seller profile for *any* user by passing the user's `user_id` in the
          request body. The target user is promoted to "seller" if necessary.
        • Duplicate seller profiles are prevented for the target user.
        """

        request_user = self.request.user  # The user making the API request

        # Determine which user the new Seller will be linked to
        target_user = request_user
        if request_user.role == 'admin':
            # Admins may specify a `user_id` in the payload to create a seller for someone else
            payload_user_id = self.request.data.get('user_id')
            if payload_user_id:
                try:
                    from .models import User  # Local import to avoid circular refs at top-level
                    target_user = User.objects.get(pk=payload_user_id)
                except User.DoesNotExist:
                    raise serializers.ValidationError({"error": "Target user not found."})

        # Prevent duplicate seller profiles for the *target* user
        if hasattr(target_user, 'seller_profile'):
            raise serializers.ValidationError({"error": "Seller profile already exists for this user."})

        # Create the seller linked to the target user
        seller = serializer.save(user_id=target_user)

        # Promote role if necessary (skip if already seller/admin)
        if target_user.role == 'customer':
            target_user.role = 'seller'
            target_user.save(update_fields=["role"])

        return seller

#allows to access, update, and delete individual sellers
class AllSellersPostRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Seller.objects.all()
    serializer_class = SellerSerializer
    lookup_field = "pk"

    def perform_destroy(self, instance):
        """Delete the seller profile and revert the linked user's role to 'customer'.

        • If the linked user currently has role 'seller', switch it back to 'customer'.
        • Admin roles are left unchanged.
        """
        linked_user = instance.user_id
        # Remove the Seller profile first
        super().perform_destroy(instance)

        # Re-evaluate the user's role
        if linked_user and linked_user.role == 'seller':
            linked_user.role = 'customer'
            linked_user.save(update_fields=["role"])

# Get products by seller  
class SellerProductsPostListCreate(generics.ListCreateAPIView):
    serializer_class = ProductSerializer

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        seller_id = self.kwargs['seller_id']
        return Product.objects.filter(seller_id=seller_id, is_deleted=False)

    def perform_create(self, serializer):
        """Create a product ensuring the authenticated user owns the seller profile"""
        seller_id_param = self.kwargs['seller_id']
        try:
            seller = Seller.objects.get(pk=seller_id_param)
        except Seller.DoesNotExist:
            raise serializers.ValidationError({"error": "Seller not found"})

        # Only the owner or admin can add products
        user = self.request.user
        if user.role != 'admin' and seller.user_id != user:
            raise serializers.ValidationError({"error": "You do not own this seller profile"})

        serializer.save(seller_id=seller)


class SellerProductPostRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    """
    Delete a specific product belonging to a seller
    """
    serializer_class = ProductSerializer
    lookup_field = 'product_id'

    def get_queryset(self):
        seller_id = self.kwargs['seller_id']
        return Product.objects.filter(seller_id=seller_id)

    def perform_destroy(self, instance):
        # Verify the product belongs to the seller
        if str(instance.seller_id.seller_id) != self.kwargs['seller_id']:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("This product does not belong to the specified seller")
        
        # Soft delete using update_fields to prevent recursion
        instance.is_deleted = True
        instance.save(update_fields=['is_deleted'])

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
    # Allow sellers or admins to access this endpoint (admins get read/delete; sellers get full access)
    permission_classes = [IsAuthenticated, IsSellerOrAdmin]

    def perform_create(self, serializer):
        """Handle the creation of a new promo with products"""
        # Get the seller associated with the user
        try:
            seller = Seller.objects.get(user_id=self.request.user)
        except Seller.DoesNotExist:
            raise serializers.ValidationError({
                "error": "Only sellers can create promos. No seller profile found for this user."
            })

        # Save the promo with the seller
        promo = serializer.save(seller_id=seller)
        
        # Get the products from the request data
        product_ids = self.request.data.get('product_id', [])
        if isinstance(product_ids, str):
            # If a single ID was provided, convert it to a list
            product_ids = [product_ids]
        
        # Validate that the products belong to this seller
        if product_ids:
            products = Product.objects.filter(
                product_id__in=product_ids,
                seller_id=seller
            )
            
            # Check if all requested products were found and belong to the seller
            found_ids = set(str(p.product_id) for p in products)
            requested_ids = set(product_ids)
            invalid_ids = requested_ids - found_ids
            
            if invalid_ids:
                raise serializers.ValidationError({
                    "error": f"Products with IDs {invalid_ids} either don't exist or don't belong to this seller."
                })
            
            # Add the products to the promo
            promo.product_id.set(products)

    def get_queryset(self):
        """Filter promos based on user role"""
        user = self.request.user
        if user.role == 'seller':
            # Sellers can only see their own promos
            return Promo.objects.filter(seller_id__user_id=user)
        elif user.role == 'admin':
            # Admins can see all promos
            return Promo.objects.all()
        else:
            # Customers can see all active promos
            return Promo.objects.filter(is_active=True)

    def delete(self, request, *args, **kwargs):
        """Bulk delete promos and ensure product discount fields are recalculated."""
        from .services.promo_services import update_product_discounted_price

        # Determine queryset based on role
        if request.user.role == 'admin':
            promos_qs = Promo.objects.all()
        elif request.user.role == 'seller':
            promos_qs = Promo.objects.filter(seller_id__user_id=request.user)
        else:
            return Response(
                {"error": "Only sellers can delete their own promos or admins can delete all promos."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Collect affected products BEFORE deletion
        from django.db.models import Prefetch
        products_to_update = set()
        for promo in promos_qs.prefetch_related('product_id'):
            products_to_update.update(list(promo.product_id.all()))

        # Delete promos in bulk
        promos_qs.delete()

        # Recalculate discounts on affected products
        for product in products_to_update:
            update_product_discounted_price(product)

        return Response(status=status.HTTP_204_NO_CONTENT)

class PromoPostRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Promo.objects.all()
    serializer_class = PromoSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "pk"

    def get_queryset(self):
        """Filter promos based on user role"""
        user = self.request.user
        if user.role == 'seller':
            # Sellers can only see their own promos
            return Promo.objects.filter(seller_id__user_id=user)
        elif user.role == 'admin':
            # Admins can see all promos
            return Promo.objects.all()
        else:
            # Customers can see all active promos
            return Promo.objects.filter(is_active=True)

    def perform_update(self, serializer):
        """Handle updating a promo's products"""
        # Get the current promo
        promo = self.get_object()
        
        # Only allow sellers to update their own promos (admins can update any)
        if self.request.user.role == 'seller' and promo.seller_id.user_id != self.request.user:
            raise serializers.ValidationError({
                "error": "You can only update your own promos."
            })
        
        # Save the promo first
        promo = serializer.save()
        
        # Get the products from the request data
        product_ids = self.request.data.get('product_id', None)
        if product_ids is not None:
            if isinstance(product_ids, str):
                # If a single ID was provided, convert it to a list
                product_ids = [product_ids]
            
            # For sellers, validate that the products belong to them
            if self.request.user.role == 'seller':
                products = Product.objects.filter(
                    product_id__in=product_ids,
                    seller_id__user_id=self.request.user
                )
                
                # Check if all requested products were found and belong to the seller
                found_ids = set(str(p.product_id) for p in products)
                requested_ids = set(product_ids)
                invalid_ids = requested_ids - found_ids
                
                if invalid_ids:
                    raise serializers.ValidationError({
                        "error": f"Products with IDs {invalid_ids} either don't exist or don't belong to you."
                    })
            else:
                # For admins, just validate that the products exist
                products = Product.objects.filter(product_id__in=product_ids)
                
                # Check if all requested products were found
                found_ids = set(str(p.product_id) for p in products)
                requested_ids = set(product_ids)
                invalid_ids = requested_ids - found_ids
                
                if invalid_ids:
                    raise serializers.ValidationError({
                        "error": f"Products with IDs {invalid_ids} don't exist."
                    })
            
            # Update the products
            promo.product_id.set(products)
        
        return promo

    def perform_destroy(self, instance):
        """Handle promo deletion with proper product updates"""
        from django.db import transaction
        
        try:
            with transaction.atomic():
                # Get all affected products before deletion
                affected_products = list(instance.product_id.all())
                
                # Delete the promo
                instance.delete()
                
                # Update each product's discount fields
                from .services.promo_services import update_product_discounted_price
                for product in affected_products:
                    update_product_discounted_price(product)
                    product.refresh_from_db()
        except Exception as e:
            raise serializers.ValidationError({
                "error": f"Error deleting promo: {str(e)}"
            })


#CART



class CartViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = CartSerializer

    def list(self, request):
        """Get user's cart summary"""
        cart = get_or_create_cart(request.user)
        serializer = self.serializer_class(cart)
        return Response(serializer.data)

    def create(self, request):
        """Add item to cart"""
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))
        
        try:
            cart_item = add_to_cart(request.user, product_id, quantity)
            return Response(
                CartItemSerializer(cart_item).data,
                status=status.HTTP_201_CREATED
            )
        except Product.DoesNotExist:
            return Response(
                {'error': 'Product not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['post'])
    def update_item(self, request):
        """Update cart item quantity"""
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 0))
        
        try:
            cart_item = update_cart_item(request.user, product_id, quantity)
            if cart_item is None:
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(CartItemSerializer(cart_item).data)
        except (Cart.DoesNotExist, CartItem.DoesNotExist):
            return Response(
                {'error': 'Cart item not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['post'])
    def remove_item(self, request):
        """Remove item from cart"""
        product_id = request.data.get('product_id')
        remove_from_cart(request.user, product_id)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['post'])
    def clear(self, request):
        """Clear all items from cart"""
        clear_cart(request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)


#ORDERS
    
class OrderPostListCreate(generics.ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def delete(self, request, *args, **kwargs):
        #deletes all orders
        Order.objects.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class OrderPostRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    lookup_field = "pk"


#ORDER ITEMS

class OrderItemPostListCreate(generics.ListCreateAPIView):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer

    def delete(self, request, *args, **kwargs):
        #deletes all order items
        OrderItem.objects.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# Add this new test view
class TestAuthView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        return Response({
            'message': 'Authentication successful!',
            'user': {
                'email': request.user.user_email,
                'role': request.user.role,
                'name': request.user.user_name
            }
        })

class DeletedUsersListDelete(generics.ListAPIView):
    """List users with is_deleted=True and allow bulk hard delete"""
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdmin]

    def get_queryset(self):
        return User.objects.filter(is_deleted=True)

    def delete(self, request, *args, **kwargs):
        count = User.objects.filter(is_deleted=True).count()
        User.objects.filter(is_deleted=True).delete()
        return Response({"deleted": count}, status=status.HTTP_204_NO_CONTENT)


class DeletedUserRetrieveDestroy(generics.RetrieveDestroyAPIView):
    """Retrieve or permanently delete a single soft-deleted user"""
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    lookup_field = "pk"

    def get_queryset(self):
        return User.objects.filter(is_deleted=True)