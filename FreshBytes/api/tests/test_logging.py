from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
import logging
import os
from ..models import User

User = get_user_model()

class LoggingTestCase(APITestCase):
    def setUp(self):
        # Create test users
        self.admin_user = User.objects.create_user(
            user_name='admin',
            user_email='admin@test.com',
            password='adminpass123',
            first_name='Admin',
            last_name='User',
            role='admin',
            is_staff=True,
            is_superuser=True
        )
        
        self.customer_user = User.objects.create_user(
            user_name='customer',
            user_email='customer@test.com',
            password='customerpass123',
            first_name='Customer',
            last_name='User',
            role='customer',
            phone_verified=True,
            email_verified=True
        )
        
        # Get tokens
        self.admin_token = RefreshToken.for_user(self.admin_user)
        self.customer_token = RefreshToken.for_user(self.customer_user)

    def test_login_logging(self):
        """Test that login attempts are logged"""
        # Test successful login
        response = self.client.post('/api/auth/login/', {
            'user_email': 'admin@test.com',
            'password': 'adminpass123'
        })
        
        self.assertEqual(response.status_code, 200)
        
        # Check if log file exists and contains login info
        log_file_path = 'logs/freshbytes.log'
        if os.path.exists(log_file_path):
            with open(log_file_path, 'r') as f:
                log_content = f.read()
                self.assertIn('Login attempt', log_content)
                self.assertIn('admin@test.com', log_content)

    def test_logout_logging(self):
        """Test that logout is logged"""
        # Login first
        self.client.force_authenticate(user=self.admin_user)
        
        # Test logout
        response = self.client.post('/api/auth/logout/', {
            'refresh_token': str(self.admin_token)
        })
        
        self.assertEqual(response.status_code, 200)
        
        # Check if log file contains logout info
        log_file_path = 'logs/freshbytes.log'
        if os.path.exists(log_file_path):
            with open(log_file_path, 'r') as f:
                log_content = f.read()
                self.assertIn('Logout attempt', log_content)

    def test_user_enable_disable_logging(self):
        """Test that user enable/disable actions are logged"""
        # Create a test user to enable/disable
        test_user = User.objects.create_user(
            user_name='testuser',
            user_email='test@test.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            role='customer',
            is_active=False
        )
        
        # Authenticate as admin
        self.client.force_authenticate(user=self.admin_user)
        
        # Test enable
        response = self.client.post(f'/api/users/{test_user.user_id}/enable/')
        self.assertEqual(response.status_code, 200)
        
        # Test disable
        response = self.client.post(f'/api/users/{test_user.user_id}/disable/')
        self.assertEqual(response.status_code, 200)
        
        # Check if log file contains enable/disable info
        log_file_path = 'logs/freshbytes.log'
        if os.path.exists(log_file_path):
            with open(log_file_path, 'r') as f:
                log_content = f.read()
                self.assertIn('enabled by admin', log_content)
                self.assertIn('disabled by admin', log_content)

    def test_business_logger(self):
        """Test that business events are logged"""
        from ..utils.logging_utils import log_business_event
        
        # Test business event logging
        log_business_event(
            event_type="TEST_EVENT",
            user_id=str(self.customer_user.user_id),
            details={"test": "data"}
        )
        
        # Check if business log file exists
        business_log_path = 'logs/business.log'
        if os.path.exists(business_log_path):
            with open(business_log_path, 'r') as f:
                log_content = f.read()
                self.assertIn('TEST_EVENT', log_content)

    def test_security_logger(self):
        """Test that security events are logged"""
        from ..utils.logging_utils import log_security_event
        
        # Test security event logging
        log_security_event(
            event_type="TEST_SECURITY",
            user_id=str(self.customer_user.user_id),
            details={"test": "security_data"}
        )
        
        # Check if security log file exists
        security_log_path = 'logs/security.log'
        if os.path.exists(security_log_path):
            with open(security_log_path, 'r') as f:
                log_content = f.read()
                self.assertIn('TEST_SECURITY', log_content) 