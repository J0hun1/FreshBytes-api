from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from ..models import Seller, Product, User
from ..serializers import SellerSerializer, ProductSerializer, UserSerializer, OrderSerializer

class AllSellersPostListCreate(generics.ListCreateAPIView):
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
                    raise serializers.ValidationError({"error": "Target user not found."})
        if hasattr(target_user, 'seller_profile'):
            raise serializers.ValidationError({"error": "Seller profile already exists for this user."})
        seller = serializer.save(user_id=target_user)
        if target_user.role == 'customer':
            target_user.role = 'seller'
            target_user.save(update_fields=["role"])
        return seller

class AllSellersPostRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Seller.objects.all()
    serializer_class = SellerSerializer
    lookup_field = "pk"
    def perform_destroy(self, instance):
        linked_user = instance.user_id
        super().perform_destroy(instance)
        if linked_user and linked_user.role == 'seller':
            linked_user.role = 'customer'
            linked_user.save(update_fields=["role"])

class SellerProductsPostListCreate(generics.ListCreateAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        seller_id = self.kwargs['seller_id']
        return Product.objects.filter(seller_id=seller_id, is_deleted=False)
    def perform_create(self, serializer):
        seller_id_param = self.kwargs['seller_id']
        try:
            seller = Seller.objects.get(pk=seller_id_param)
        except Seller.DoesNotExist:
            raise serializers.ValidationError({"error": "Seller not found"})
        user = self.request.user
        if user.role != 'admin' and seller.user_id != user:
            raise serializers.ValidationError({"error": "You do not own this seller profile"})
        serializer.save(seller_id=seller)

class SellerProductPostRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProductSerializer
    lookup_field = 'product_id'
    def get_queryset(self):
        seller_id = self.kwargs['seller_id']
        return Product.objects.filter(seller_id=seller_id)
    def perform_destroy(self, instance):
        if str(instance.seller_id.seller_id) != self.kwargs['seller_id']:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("This product does not belong to the specified seller")
        instance.is_deleted = True
        instance.save(update_fields=['is_deleted'])

class SellerCustomersView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, seller_id):
        seller = Seller.objects.get(pk=seller_id)
        customers = seller.get_customers()
        data = UserSerializer(customers, many=True).data
        return Response(data)

class SellerTransactionsView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, seller_id):
        seller = Seller.objects.get(pk=seller_id)
        transactions = seller.get_transactions()
        data = OrderSerializer(transactions, many=True).data
        return Response(data)

class SellerProductsBoughtByCustomerView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, seller_id, customer_id):
        seller = Seller.objects.get(pk=seller_id)
        products = seller.get_products_bought_by_customer(customer_id)
        data = ProductSerializer(products, many=True).data
        return Response(data)
