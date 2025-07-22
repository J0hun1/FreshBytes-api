from rest_framework import generics, status
from rest_framework.response import Response
from ..models import SubCategory
from ..serializers import SubCategorySerializer

class SubCategoryPostListCreate(generics.ListCreateAPIView):
    queryset = SubCategory.objects.all()
    serializer_class = SubCategorySerializer
    def delete(self, request, *args, **kwargs):
        SubCategory.objects.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class SubCategoryPostRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = SubCategory.objects.all()
    serializer_class = SubCategorySerializer
    lookup_field = "pk" 