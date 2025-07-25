from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from ..models import Order, OrderItem
from ..serializers import OrderSerializer, OrderItemSerializer, PaymentSerializer
from ..services.order_services import create_order_from_cart
from ..services.seller_services import update_seller_stats_on_order_delivered
from drf_spectacular.utils import extend_schema, extend_schema_view
from ..permissions import IsSellerGroup, IsAdminGroup

@extend_schema(tags=['Order'])

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'order_id'

    def get_object(self):
        order_number = self.kwargs.get('order_number')
        if order_number:
            return get_object_or_404(Order, order_number=order_number)
        return super().get_object()

    @action(detail=False, methods=['post'])
    def checkout(self, request):
        cart_item_ids = request.data.get('cart_item_ids', None)
        payment_method = request.data.get('payment_method', None)
        try:
            order, payment = create_order_from_cart(request.user, cart_item_ids, payment_method)
            return Response({
                "order": OrderSerializer(order).data,
                "payment": PaymentSerializer(payment).data
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    ALLOWED_TRANSITIONS = {
        'PENDING': ['CONFIRMED', 'CANCELLED'],
        'CONFIRMED': ['SHIPPED', 'CANCELLED'],
        'SHIPPED': ['DELIVERED'],
        'DELIVERED': [],
        'CANCELLED': [],
    }

    @action(detail=True, methods=['patch'], permission_classes=[IsAuthenticated, IsSellerGroup, IsAdminGroup])
    def update_status(self, request, order_id=None):
        order = self.get_object()
        user = request.user
        is_admin = user.groups.filter(name='Admin').exists()
        is_order_owner = (order.user_id == user)
        is_seller = False
        if hasattr(user, 'seller_profile'):
            seller = user.seller_profile
            is_seller = OrderItem.objects.filter(order_id=order, product_id__seller_id=seller).exists()
        new_status = request.data.get('order_status')
        allowed_statuses = [choice[0] for choice in Order._meta.get_field('order_status').choices]
        if new_status not in allowed_statuses:
            return Response({'error': f'Invalid status. Allowed: {allowed_statuses}'}, status=status.HTTP_400_BAD_REQUEST)
        old_status = order.order_status
        # Enforce allowed transitions
        if new_status not in self.ALLOWED_TRANSITIONS.get(old_status, []):
            return Response({'error': f'Cannot change status from {old_status} to {new_status}.'}, status=status.HTTP_400_BAD_REQUEST)
        if is_order_owner and new_status == 'CANCELLED':
            if order.order_status == 'PENDING':
                order.order_status = 'CANCELLED'
                order.save(update_fields=['order_status', 'updated_at'])
                return Response(OrderSerializer(order).data, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'You can only cancel orders that are still PENDING.'}, status=status.HTTP_403_FORBIDDEN)
        if not (is_admin or is_seller):
            return Response({'error': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)
        order.order_status = new_status
        order.save(update_fields=['order_status', 'updated_at'])
        if old_status != 'DELIVERED' and new_status == 'DELIVERED':
            update_seller_stats_on_order_delivered(order)
        return Response(OrderSerializer(order).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['patch'], permission_classes=[IsAuthenticated, IsSellerGroup, IsAdminGroup])
    def archive(self, request, order_id=None):
        order = self.get_object()
        user = request.user
        is_admin = user.groups.filter(name='Admin').exists()
        is_order_owner = (order.user_id == user)
        if not (is_admin or is_order_owner):
            return Response({'error': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)
        is_archived = request.data.get('is_archived')
        if is_archived is None:
            return Response({'error': 'is_archived field is required.'}, status=status.HTTP_400_BAD_REQUEST)
        order.is_archived = bool(is_archived)
        order.save(update_fields=['is_archived', 'updated_at'])
        return Response(OrderSerializer(order).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='archived')
    def archived_orders(self, request):
        archived = Order.objects.filter(is_archived=True)
        serializer = self.get_serializer(archived, many=True)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        return Response({'detail': 'Order deletion is not allowed.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@extend_schema(tags=['OrderItem'])

class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['delete'])
    def delete_all(self, request):
        OrderItem.objects.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
