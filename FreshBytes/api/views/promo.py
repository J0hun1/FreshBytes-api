from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from ..models import Promo, Product, Seller
from ..serializers import PromoSerializer, ProductSerializer

class PromoViewSet(viewsets.ModelViewSet):
    queryset = Promo.objects.all()
    serializer_class = PromoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'seller':
            return Promo.objects.filter(seller_id__user_id=user)
        elif user.role == 'admin':
            return Promo.objects.all()
        else:
            return Promo.objects.filter(is_active=True)

    def perform_create(self, serializer):
        try:
            seller = Seller.objects.get(user_id=self.request.user)
        except Seller.DoesNotExist:
            from rest_framework import serializers
            raise serializers.ValidationError({"error": "Only sellers can create promos. No seller profile found for this user."})
        promo = serializer.save(seller_id=seller)
        product_ids = self.request.data.get('product_id', [])
        if isinstance(product_ids, str):
            product_ids = [product_ids]
        if product_ids:
            products = Product.objects.filter(
                product_id__in=product_ids,
                seller_id=seller
            )
            found_ids = set(str(p.product_id) for p in products)
            requested_ids = set(product_ids)
            invalid_ids = requested_ids - found_ids
            if invalid_ids:
                from rest_framework import serializers
                raise serializers.ValidationError({"error": f"Products with IDs {invalid_ids} either don't exist or don't belong to this seller."})
            promo.product_id.set(products)
        return promo

    def perform_update(self, serializer):
        promo = self.get_object()
        if self.request.user.role == 'seller' and promo.seller_id.user_id != self.request.user:
            from rest_framework import serializers
            raise serializers.ValidationError({"error": "You can only update your own promos."})
        promo = serializer.save()
        product_ids = self.request.data.get('product_id', None)
        if product_ids is not None:
            if isinstance(product_ids, str):
                product_ids = [product_ids]
            if self.request.user.role == 'seller':
                products = Product.objects.filter(
                    product_id__in=product_ids,
                    seller_id__user_id=self.request.user
                )
                found_ids = set(str(p.product_id) for p in products)
                requested_ids = set(product_ids)
                invalid_ids = requested_ids - found_ids
                if invalid_ids:
                    from rest_framework import serializers
                    raise serializers.ValidationError({"error": f"Products with IDs {invalid_ids} either don't exist or don't belong to you."})
            else:
                products = Product.objects.filter(product_id__in=product_ids)
                found_ids = set(str(p.product_id) for p in products)
                requested_ids = set(product_ids)
                invalid_ids = requested_ids - found_ids
                if invalid_ids:
                    from rest_framework import serializers
                    raise serializers.ValidationError({"error": f"Products with IDs {invalid_ids} don't exist."})
            promo.product_id.set(products)
        return promo

    def perform_destroy(self, instance):
        from django.db import transaction
        try:
            with transaction.atomic():
                affected_products = list(instance.product_id.all())
                instance.delete()
                from ..services.promo_services import update_product_discounted_price
                for product in affected_products:
                    update_product_discounted_price(product)
                    product.refresh_from_db()
        except Exception as e:
            from rest_framework import serializers
            raise serializers.ValidationError({"error": f"Error deleting promo: {str(e)}"})

    @action(detail=False, methods=['delete'])
    def delete_all(self, request):
        from ..services.promo_services import update_product_discounted_price
        if request.user.role == 'admin':
            promos_qs = Promo.objects.all()
        elif request.user.role == 'seller':
            promos_qs = Promo.objects.filter(seller_id__user_id=request.user)
        else:
            return Response({"error": "Only sellers can delete their own promos or admins can delete all promos."}, status=status.HTTP_403_FORBIDDEN)
        from django.db.models import Prefetch
        products_to_update = set()
        for promo in promos_qs.prefetch_related('product_id'):
            products_to_update.update(list(promo.product_id.all()))
        promos_qs.delete()
        for product in products_to_update:
            update_product_discounted_price(product)
        return Response(status=status.HTTP_204_NO_CONTENT)
