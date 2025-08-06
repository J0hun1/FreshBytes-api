from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from ..models import Payment
from ..serializers import PaymentSerializer
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser
import logging
from ..utils.logging_utils import log_business_event, log_security_event

# Get logger for this module
logger = logging.getLogger(__name__)

@extend_schema(tags=['Payment'])
class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'payment_id'

    @action(detail=True, methods=['patch'], url_path='update_status', permission_classes=[IsAdminUser])
    def update_status(self, request, payment_id=None):
        """Enhanced payment status update with business transaction logging"""
        try:
            payment = self.get_object()
            admin_user = request.user
            old_status = payment.payment_status
            new_status = request.data.get('payment_status')
            
            # Log the status change attempt
            logger.info(f"Payment status change attempt: {payment_id} from {old_status} to {new_status} by admin {admin_user.user_name}")
            
            allowed_statuses = [choice[0] for choice in payment.PAYMENT_STATUS]
            if new_status not in allowed_statuses:
                logger.warning(f"Invalid payment status '{new_status}' attempted by admin {admin_user.user_name}")
                return Response({'error': f'Invalid status. Allowed: {allowed_statuses}'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Optionally: Only allow certain transitions (e.g., PENDING -> COMPLETED/FAILED, COMPLETED -> REFUNDED)
            valid_transitions = {
                'PENDING': ['COMPLETED', 'FAILED'],
                'COMPLETED': ['REFUNDED'],
                'FAILED': [],
                'REFUNDED': [],
            }
            
            if new_status not in valid_transitions.get(payment.payment_status, []):
                logger.warning(f"Invalid payment status transition from {old_status} to {new_status} by admin {admin_user.user_name}")
                return Response({'error': f'Cannot change status from {payment.payment_status} to {new_status}.'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Log the business event
            log_business_event(
                event_type="PAYMENT_STATUS_CHANGED",
                user_id=str(payment.user_id.user_id) if payment.user_id else None,
                admin_user_id=str(admin_user.user_id),
                details={
                    "payment_id": str(payment.payment_id),
                    "order_id": str(payment.order_id.order_id) if payment.order_id else None,
                    "old_status": old_status,
                    "new_status": new_status,
                    "amount": str(payment.payment_amount) if payment.payment_amount else None,
                    "admin_user": admin_user.user_name
                }
            )
            
            payment.payment_status = new_status
            payment.save(update_fields=['payment_status', 'updated_at'])
            
            # Log successful status change
            logger.info(f"Payment {payment_id} status successfully changed from {old_status} to {new_status} by admin {admin_user.user_name}")
            
            # Optionally: update order status or trigger refund logic here
            return Response(self.get_serializer(payment).data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error updating payment status for payment {payment_id}: {str(e)}")
            raise
