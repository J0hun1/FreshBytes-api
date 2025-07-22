from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from ..models import Product
from ..serializers import ProductSerializer

class ProductPostListCreate(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def delete(self, request, *args, **kwargs):
        Product.objects.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class ProductPostRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = "pk"

class ProductSoftDeleteView(APIView):
    def patch(self, request, product_id):
        try:
            product = Product.all_objects.get(product_id=product_id)
            if product.is_deleted:
                return Response({'detail': 'Product already deleted.'}, status=status.HTTP_400_BAD_REQUEST)
            product.is_deleted = True
            product.save()
            return Response({'detail': 'Product soft-deleted.'}, status=status.HTTP_200_OK)
        except Product.DoesNotExist:
            return Response({'detail': 'Product not found.'}, status=status.HTTP_404_NOT_FOUND)

class ProductRestoreView(APIView):
    def patch(self, request, product_id):
        try:
            product = Product.all_objects.get(product_id=product_id)
            if not product.is_deleted:
                return Response({'detail': 'Product is not deleted.'}, status=status.HTTP_400_BAD_REQUEST)
            product.is_deleted = False
            product.save()
            return Response({'detail': 'Product restored.'}, status=status.HTTP_200_OK)
        except Product.DoesNotExist:
            return Response({'detail': 'Product not found.'}, status=status.HTTP_404_NOT_FOUND)

class DeletedProductListView(APIView):
    def get(self, request):
        deleted_products = Product.all_objects.filter(is_deleted=True)
        data = [
            {
                'product_id': p.product_id,
                'product_name': p.product_name,
                'is_deleted': p.is_deleted
            } for p in deleted_products
        ]
        return Response(data, status=status.HTTP_200_OK)
