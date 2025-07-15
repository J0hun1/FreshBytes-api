from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db import transaction
from ..models import User, Product, ApprovalStatus

def create_approval_record(obj, content_type):
    """
    Create an approval status record for a new user or product
    """
    return ApprovalStatus.objects.create(
        content_type=content_type,
        object_id=str(obj.user_id if content_type == 'user' else obj.product_id),
        status='PENDING'
    )

@transaction.atomic
def process_approval(obj, content_type, status, reviewed_by, notes=None):
    """
    Process an approval/rejection for a user or product
    
    Args:
        obj: User or Product instance
        content_type: 'user' or 'product'
        status: 'APPROVED' or 'REJECTED'
        reviewed_by: User instance of the admin
        notes: Optional notes about the decision
    """
    if not reviewed_by.is_staff:
        raise ValidationError("Only staff members can process approvals")

    # Update the object's status
    obj.approval_status = status
    
    if content_type == 'user':
        # For users, handle activation based on approval
        if status == 'APPROVED':
            obj.is_active = True
        else:
            obj.is_active = False
            
    elif content_type == 'product':
        # For products, handle visibility based on approval
        if status == 'APPROVED':
            obj.is_active = True
        else:
            obj.is_active = False
    
    obj.save()

    # Create approval history record
    ApprovalStatus.objects.create(
        content_type=content_type,
        object_id=str(obj.user_id if content_type == 'user' else obj.product_id),
        status=status,
        reviewed_by=reviewed_by,
        reviewed_at=timezone.now(),
        notes=notes
    )

def get_pending_approvals(content_type=None):
    """
    Get all pending approvals, optionally filtered by content type
    """
    queryset = ApprovalStatus.objects.filter(status='PENDING')
    if content_type:
        queryset = queryset.filter(content_type=content_type)
    return queryset.order_by('created_at')

def get_approval_history(obj, content_type):
    """
    Get approval history for a specific object
    """
    return ApprovalStatus.objects.filter(
        content_type=content_type,
        object_id=str(obj.user_id if content_type == 'user' else obj.product_id)
    ).order_by('-created_at') 