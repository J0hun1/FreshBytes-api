from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims
        token['user_email'] = user.user_email
        token['role'] = user.role  # Keep for backward compatibility
        token['user_name'] = user.user_name
        
        # Add group information for new permission system
        token['groups'] = [group.name for group in user.groups.all()]
        token['primary_role'] = user.get_primary_role()
        
        # Add some key permissions for quick frontend checks
        token['permissions'] = {
            'can_manage_products': user.has_perm('api.add_product') and user.has_perm('api.change_product'),
            'can_approve_products': user.has_perm('api.can_approve_products'),
            'can_view_seller_stats': user.has_perm('api.can_view_seller_stats'),
            'can_manage_users': user.has_perm('api.can_manage_sellers'),
            'is_admin': user.is_admin(),
            'is_seller': user.is_seller(),
            'is_customer': user.is_customer()
        }
        
        return token 