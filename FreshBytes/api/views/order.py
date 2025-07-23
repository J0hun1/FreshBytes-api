from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from ..models import Order, OrderItem
from ..serializers import OrderSerializer, OrderItemSerializer
from ..services.order_services import create_order_from_cart
from ..services.seller_services import update_seller_stats_on_order_delivered

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
        try:
            order = create_order_from_cart(request.user, cart_item_ids)
            return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['patch'])
    def update_status(self, request, order_id=None):
        order = self.get_object()
        user = request.user
        is_admin = user.is_admin() if hasattr(user, 'is_admin') else (user.role == 'admin')
        is_order_owner = (order.user_id == user)
        is_seller = False
        if hasattr(user, 'seller_profile'):
            seller = user.seller_profile
            is_seller = OrderItem.objects.filter(order_id=order, product_id__seller_id=seller).exists()
        new_status = request.data.get('order_status')
        allowed_statuses = [choice[0] for choice in Order._meta.get_field('order_status').choices]
        if new_status not in allowed_statuses:
            return Response({'error': f'Invalid status. Allowed: {allowed_statuses}'}, status=status.HTTP_400_BAD_REQUEST)
        if is_order_owner and new_status == 'CANCELLED':
            if order.order_status == 'PENDING':
                order.order_status = 'CANCELLED'
                order.save(update_fields=['order_status', 'updated_at'])
                return Response(OrderSerializer(order).data, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'You can only cancel orders that are still PENDING.'}, status=status.HTTP_403_FORBIDDEN)
        if not (is_admin or is_seller):
            return Response({'error': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)
        old_status = order.order_status
        order.order_status = new_status
        order.save(update_fields=['order_status', 'updated_at'])
        if old_status != 'DELIVERED' and new_status == 'DELIVERED':
            update_seller_stats_on_order_delivered(order)
        return Response(OrderSerializer(order).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['patch'])
    def archive(self, request, order_id=None):
        order = self.get_object()
        user = request.user
        is_admin = user.is_admin() if hasattr(user, 'is_admin') else (user.role == 'admin')
        is_order_owner = (order.user_id == user)
        if not (is_admin or is_order_owner):
            return Response({'error': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)
        is_archived = request.data.get('is_archived')
        if is_archived is None:
            return Response({'error': 'is_archived field is required.'}, status=status.HTTP_400_BAD_REQUEST)
        order.is_archived = bool(is_archived)
        order.save(update_fields=['is_archived', 'updated_at'])
        return Response(OrderSerializer(order).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['delete'])
    def delete_all(self, request):
        Order.objects.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['delete'])
    def delete_all(self, request):
        OrderItem.objects.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
