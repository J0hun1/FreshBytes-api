from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from ..models import Category
from ..serializers import CategorySerializer

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    @action(detail=False, methods=['delete'])
    def delete_all(self, request):
        Category.objects.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT) 