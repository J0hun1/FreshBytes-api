from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from ..models import Product
from ..serializers import ProductSerializer
from drf_spectacular.utils import extend_schema, extend_schema_view

@extend_schema(tags=['Product'])

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    # Industry-standard query parameter support:
    # Filtering: product_price, seller_id, is_deleted, is_active, product_name
    # Searching: product_name
    # Ordering: product_price, created_at
    filterset_fields = ['product_price', 'seller_id', 'is_deleted', 'is_active', 'product_name']
    search_fields = ['product_name']
    ordering_fields = ['product_price', 'created_at']
    ordering = ['-created_at']  # Default ordering: newest first

    @action(detail=True, methods=['patch'])
    def soft_delete(self, request, pk=None):
        product = self.get_object()
        if product.is_deleted:
            return Response({'detail': 'Product already deleted.'}, status=status.HTTP_400_BAD_REQUEST)
        product.is_deleted = True
        product.save()
        return Response({'detail': 'Product soft-deleted.'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['patch'])
    def restore(self, request, pk=None):
        product = self.get_object()
        if not product.is_deleted:
            return Response({'detail': 'Product is not deleted.'}, status=status.HTTP_400_BAD_REQUEST)
        product.is_deleted = False
        product.save()
        return Response({'detail': 'Product restored.'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def deleted(self, request):
        deleted_products = Product.all_objects.filter(is_deleted=True)
        data = ProductSerializer(deleted_products, many=True).data
        return Response(data, status=status.HTTP_200_OK)