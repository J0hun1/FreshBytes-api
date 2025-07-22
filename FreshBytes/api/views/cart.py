from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from ..models import Cart, CartItem, Product
from ..serializers import CartSerializer, CartItemSerializer
from ..services.cart_services import get_or_create_cart, add_to_cart, update_cart_item, remove_from_cart, clear_cart

class CartViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = CartSerializer

    def list(self, request):
        cart = get_or_create_cart(request.user)
        serializer = self.serializer_class(cart)
        return Response(serializer.data)

    def create(self, request):
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
        product_id = request.data.get('product_id')
        remove_from_cart(request.user, product_id)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['post'])
    def clear(self, request):
        clear_cart(request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)
