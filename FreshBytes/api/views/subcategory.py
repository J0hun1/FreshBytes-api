from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from ..models import SubCategory
from ..serializers import SubCategorySerializer

class SubCategoryViewSet(viewsets.ModelViewSet):
    queryset = SubCategory.objects.all()
    serializer_class = SubCategorySerializer

    @action(detail=False, methods=['delete'])
    def delete_all(self, request):
        SubCategory.objects.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT) 