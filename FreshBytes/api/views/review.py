from rest_framework import generics, status
from rest_framework.response import Response
from ..models import Reviews
from ..serializers import ReviewsSerializer

class ReviewsPostListCreate(generics.ListCreateAPIView):
    queryset = Reviews.objects.all()
    serializer_class = ReviewsSerializer
    def delete(self, request, *args, **kwargs):
        Reviews.objects.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class ReviewsPostRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Reviews.objects.all()
    serializer_class = ReviewsSerializer
    lookup_field = "pk"
