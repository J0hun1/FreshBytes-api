from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, BasePermission
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import get_object_or_404
from django.utils import timezone
from ..models import User
from ..serializers import UserSerializer, CustomTokenObtainPairSerializer
from ..permissions import IsAdmin, IsSeller, IsCustomer
from drf_spectacular.utils import extend_schema, extend_schema_view


class CustomTokenObtainPairView(TokenObtainPairView):
    permission_classes = [AllowAny]
    serializer_class = CustomTokenObtainPairSerializer

@extend_schema(tags=['AdminDashboard'])
class AdminDashboardView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]
    

    def get(self, request):
        # Example admin data
        data = {
            "message": "Welcome, admin!",
            "stats": {
                # ... your admin dashboard data here ...
            }
        }
        return Response(data)
@extend_schema(tags=['UserRegister'])
class RegisterView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    queryset = User.objects.all()
    serializer_class = UserSerializer

@extend_schema(tags=['UserLogout'])
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Successfully logged out."}, status=status.HTTP_200_OK)
        except Exception:
            return Response({"error": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=['User'])
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "pk"

    def get_queryset(self):
        user = self.request.user
        if self.action in ["list", "retrieve", "update", "partial_update", "destroy"]:
            if user.role == 'admin':
                return User.objects.all()
            return User.objects.filter(user_id=user.user_id)
        return super().get_queryset()

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.is_active = False
        instance.save()

    @action(detail=True, methods=['post'])
    def enable(self, request, pk=None):
        user = get_object_or_404(User, pk=pk, is_deleted=False)
        if user.is_active:
            return Response({"detail": "User already active."}, status=400)
        user.is_active = True
        user.save(update_fields=["is_active"])
        return Response(UserSerializer(user).data, status=200)

    @action(detail=True, methods=['post'])
    def disable(self, request, pk=None):
        user = get_object_or_404(User, pk=pk, is_deleted=False)
        if not user.is_active:
            return Response({"detail": "User already inactive."}, status=400)
        user.is_active = False
        user.save(update_fields=["is_active"])
        return Response({"detail": "User disabled."}, status=200)

    @action(detail=True, methods=['post'])
    def restore(self, request, pk=None):
        try:
            user = User.objects.get(pk=pk, is_deleted=True)
        except User.DoesNotExist:
            return Response({"error": "User not found or not deleted."}, status=status.HTTP_404_NOT_FOUND)
        user.is_deleted = False
        user.is_active = True
        user.save(update_fields=["is_deleted", "is_active"])
        return Response(UserSerializer(user).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get', 'delete'])
    def deleted(self, request):
        if request.method == 'GET':
            users = User.objects.filter(is_deleted=True)
            serializer = self.get_serializer(users, many=True)
            return Response(serializer.data)
        elif request.method == 'DELETE':
            count = User.objects.filter(is_deleted=True).count()
            User.objects.filter(is_deleted=True).delete()
            return Response({"deleted": count}, status=status.HTTP_204_NO_CONTENT)

@extend_schema(tags=['UserDeleted'])
class DeletedUserRetrieveDestroy(generics.RetrieveDestroyAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, BasePermission]
    lookup_field = "pk"
    def get_queryset(self):
        return User.objects.filter(is_deleted=True)

@extend_schema(tags=['UserPermissions'])
class UserPermissionsView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]
    def get(self, request):
        user = request.user
        user_permissions = list(user.get_all_permissions())
        group_permissions = []
        for group in user.groups.all():
            group_permissions.extend([
                f"{perm.content_type.app_label}.{perm.codename}" 
                for perm in group.permissions.all()
            ])
        return Response({
            'user_id': str(user.user_id),
            'email': user.user_email,
            'role': user.role,
            'primary_role': user.get_primary_role(),
            'groups': [group.name for group in user.groups.all()],
            'permissions': {
                'all_permissions': user_permissions,
                'group_permissions': list(set(group_permissions)),
                'role_checks': {
                    'is_admin': user.is_admin(),
                    'is_seller': user.is_seller(),
                    'is_customer': user.is_customer(),
                },
                'specific_permissions': {
                    'can_add_product': user.has_perm('api.add_product'),
                    'can_change_product': user.has_perm('api.change_product'),
                    'can_delete_product': user.has_perm('api.delete_product'),
                    'can_approve_products': user.has_perm('api.can_approve_products'),
                    'can_feature_products': user.has_perm('api.can_feature_products'),
                    'can_view_seller_stats': user.has_perm('api.can_view_seller_stats'),
                    'can_manage_sellers': user.has_perm('api.can_manage_sellers'),
                    'can_moderate_reviews': user.has_perm('api.can_moderate_reviews'),
                    'can_view_all_orders': user.has_perm('api.can_view_all_orders'),
                }
            }
        })
    def post(self, request):
        permission = request.data.get('permission')
        if not permission:
            return Response({'error': 'Permission parameter is required'}, status=status.HTTP_400_BAD_REQUEST)
        if '.' not in permission:
            permission = f'api.{permission}'
        has_permission = request.user.has_perm(permission)
        return Response({
            'permission': permission,
            'has_permission': has_permission,
            'user_id': str(request.user.user_id),
            'checked_at': timezone.now().isoformat()
        })
