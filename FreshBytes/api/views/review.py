from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from ..models import Reviews
from ..serializers import ReviewsSerializer
from drf_spectacular.utils import extend_schema, extend_schema_view

@extend_schema(tags=['Reviews'])

class ReviewsViewSet(viewsets.ModelViewSet):
    queryset = Reviews.objects.all()
    serializer_class = ReviewsSerializer

    @action(detail=False, methods=['delete'])
    def delete_all(self, request):
        Reviews.objects.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
