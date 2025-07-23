from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from ..models import Reviews
from ..serializers import ReviewsSerializer

class ReviewsViewSet(viewsets.ModelViewSet):
    queryset = Reviews.objects.all()
    serializer_class = ReviewsSerializer

    @action(detail=False, methods=['delete'])
    def delete_all(self, request):
        Reviews.objects.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
