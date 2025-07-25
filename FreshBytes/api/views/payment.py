from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from ..models import Payment
from ..serializers import PaymentSerializer
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser

@extend_schema(tags=['Payment'])
class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'payment_id'

    @action(detail=True, methods=['patch'], url_path='update_status', permission_classes=[IsAdminUser])
    def update_status(self, request, payment_id=None):
        payment = self.get_object()
        new_status = request.data.get('payment_status')
        allowed_statuses = [choice[0] for choice in payment.PAYMENT_STATUS]
        if new_status not in allowed_statuses:
            return Response({'error': f'Invalid status. Allowed: {allowed_statuses}'}, status=status.HTTP_400_BAD_REQUEST)
        # Optionally: Only allow certain transitions (e.g., PENDING -> COMPLETED/FAILED, COMPLETED -> REFUNDED)
        valid_transitions = {
            'PENDING': ['COMPLETED', 'FAILED'],
            'COMPLETED': ['REFUNDED'],
            'FAILED': [],
            'REFUNDED': [],
        }
        if new_status not in valid_transitions.get(payment.payment_status, []):
            return Response({'error': f'Cannot change status from {payment.payment_status} to {new_status}.'}, status=status.HTTP_400_BAD_REQUEST)
        payment.payment_status = new_status
        payment.save(update_fields=['payment_status', 'updated_at'])
        # Optionally: update order status or trigger refund logic here
        return Response(self.get_serializer(payment).data, status=status.HTTP_200_OK)
