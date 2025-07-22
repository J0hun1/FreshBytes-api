from rest_framework import generics, status
from rest_framework.response import Response
from ..models import Category
from ..serializers import CategorySerializer

class CategoryPostListCreate(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    def delete(self, request, *args, **kwargs):
        Category.objects.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class CategoryPostRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = "pk" 