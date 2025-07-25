from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from ..models import Seller, Product, User
from ..serializers import SellerSerializer, ProductSerializer, UserSerializer, OrderSerializer
from drf_spectacular.utils import extend_schema, extend_schema_view


@extend_schema(tags=['Seller'])

class SellerViewSet(viewsets.ModelViewSet):
    queryset = Seller.objects.all()  
    serializer_class = SellerSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        request_user = self.request.user
        target_user = request_user
        if request_user.role == 'admin':
            payload_user_id = self.request.data.get('user_id')
            if payload_user_id:
                try:
                    target_user = User.objects.get(pk=payload_user_id)
                except User.DoesNotExist:
                    from rest_framework import serializers
                    raise serializers.ValidationError({"error": "Target user not found."})
        if hasattr(target_user, 'seller_profile'):
            from rest_framework import serializers
            raise serializers.ValidationError({"error": "Seller profile already exists for this user."})
        seller = serializer.save(user_id=target_user)
        if target_user.role == 'customer':
            target_user.role = 'seller'
            target_user.save(update_fields=["role"])
        return seller

    def perform_destroy(self, instance):
        linked_user = instance.user_id
        super().perform_destroy(instance)
        if linked_user and linked_user.role == 'seller':
            linked_user.role = 'customer'
            linked_user.save(update_fields=["role"])

    @action(detail=True, methods=['get', 'post'], url_path='products')
    def products(self, request, pk=None):
        seller = self.get_object()
        if request.method == 'GET':
            products = Product.objects.filter(seller_id=seller, is_deleted=False)
            serializer = ProductSerializer(products, many=True)
            return Response(serializer.data)
        elif request.method == 'POST':
            user = request.user
            if user.role != 'admin' and seller.user_id != user:
                from rest_framework import serializers
                raise serializers.ValidationError({"error": "You do not own this seller profile"})
            serializer = ProductSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(seller_id=seller)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'], url_path='products/(?P<product_id>[^/.]+)')
    def product_detail(self, request, pk=None, product_id=None):
        seller = self.get_object()
        product = get_object_or_404(Product, pk=product_id, seller_id=seller)
        if request.method == 'GET':
            serializer = ProductSerializer(product)
            return Response(serializer.data)

    @action(detail=True, methods=['delete'], url_path='products/(?P<product_id>[^/.]+)')
    def product_delete(self, request, pk=None, product_id=None):
        seller = self.get_object()
        product = get_object_or_404(Product, pk=product_id, seller_id=seller)
        product.is_deleted = True
        product.save(update_fields=['is_deleted'])
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['get'])
    def customers(self, request, pk=None):
        seller = self.get_object()
        customers = seller.get_customers()
        data = UserSerializer(customers, many=True).data
        return Response(data)

    @action(detail=True, methods=['get'])
    def transactions(self, request, pk=None):
        seller = self.get_object()
        transactions = seller.get_transactions()
        data = OrderSerializer(transactions, many=True).data
        return Response(data)

    @action(detail=True, methods=['get'], url_path='customers/(?P<customer_id>[^/.]+)/products')
    def products_bought_by_customer(self, request, pk=None, customer_id=None):
        seller = self.get_object()
        products = seller.get_products_bought_by_customer(customer_id)
        data = ProductSerializer(products, many=True).data
        return Response(data)
