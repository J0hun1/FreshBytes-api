from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from ..utils.verification import check_user_verification, get_verification_status, get_verification_message

User = get_user_model()

class VerificationTestCase(APITestCase):
    def setUp(self):
        # Create test users with different verification statuses
        self.user_unverified = User.objects.create_user(
            user_name='testuser1',
            user_email='test1@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User1',
            user_phone='09123456789',
            phone_verified=False,
            email_verified=False
        )
        
        self.user_phone_verified = User.objects.create_user(
            user_name='testuser2',
            user_email='test2@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User2',
            user_phone='09123456788',
            phone_verified=True,
            email_verified=False
        )
        
        self.user_email_verified = User.objects.create_user(
            user_name='testuser3',
            user_email='test3@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User3',
            user_phone='09123456787',
            phone_verified=False,
            email_verified=True
        )
        
        self.user_fully_verified = User.objects.create_user(
            user_name='testuser4',
            user_email='test4@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User4',
            user_phone='09123456786',
            phone_verified=True,
            email_verified=True
        )

    def test_verification_utility_functions(self):
        """Test verification utility functions"""
        # Test unverified user
        with self.assertRaises(Exception):
            check_user_verification(self.user_unverified, require_both=False)
        
        # Test phone verified user (should pass)
        self.assertTrue(check_user_verification(self.user_phone_verified, require_both=False))
        
        # Test email verified user (should pass)
        self.assertTrue(check_user_verification(self.user_email_verified, require_both=False))
        
        # Test fully verified user (should pass)
        self.assertTrue(check_user_verification(self.user_fully_verified, require_both=False))
        
        # Test fully verified user with require_both=True (should pass)
        self.assertTrue(check_user_verification(self.user_fully_verified, require_both=True))
        
        # Test partially verified users with require_both=True (should fail)
        with self.assertRaises(Exception):
            check_user_verification(self.user_phone_verified, require_both=True)
        
        with self.assertRaises(Exception):
            check_user_verification(self.user_email_verified, require_both=True)

    def test_verification_status_api(self):
        """Test verification status API endpoint"""
        # Test unverified user
        self.client.force_authenticate(user=self.user_unverified)
        response = self.client.get('/api/auth/verification-status/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.data
        self.assertFalse(data['verification_status']['phone_verified'])
        self.assertFalse(data['verification_status']['email_verified'])
        self.assertFalse(data['verification_status']['fully_verified'])
        self.assertFalse(data['verification_status']['partially_verified'])
        self.assertTrue(data['verification_status']['verification_required'])
        self.assertFalse(data['can_perform_actions']['can_add_to_cart'])
        self.assertFalse(data['can_perform_actions']['can_make_reviews'])
        self.assertFalse(data['can_perform_actions']['can_make_transactions'])
        self.assertTrue(data['can_perform_actions']['can_view_products'])
        self.assertTrue(data['can_perform_actions']['can_login'])

    def test_verification_status_utility_functions(self):
        """Test verification status utility functions"""
        # Test unverified user
        status_unverified = get_verification_status(self.user_unverified)
        self.assertFalse(status_unverified['phone_verified'])
        self.assertFalse(status_unverified['email_verified'])
        self.assertFalse(status_unverified['fully_verified'])
        self.assertFalse(status_unverified['partially_verified'])
        self.assertTrue(status_unverified['verification_required'])
        
        # Test phone verified user
        status_phone = get_verification_status(self.user_phone_verified)
        self.assertTrue(status_phone['phone_verified'])
        self.assertFalse(status_phone['email_verified'])
        self.assertFalse(status_phone['fully_verified'])
        self.assertTrue(status_phone['partially_verified'])
        self.assertFalse(status_phone['verification_required'])
        
        # Test email verified user
        status_email = get_verification_status(self.user_email_verified)
        self.assertFalse(status_email['phone_verified'])
        self.assertTrue(status_email['email_verified'])
        self.assertFalse(status_email['fully_verified'])
        self.assertTrue(status_email['partially_verified'])
        self.assertFalse(status_email['verification_required'])
        
        # Test fully verified user
        status_fully = get_verification_status(self.user_fully_verified)
        self.assertTrue(status_fully['phone_verified'])
        self.assertTrue(status_fully['email_verified'])
        self.assertTrue(status_fully['fully_verified'])
        self.assertTrue(status_fully['partially_verified'])
        self.assertFalse(status_fully['verification_required'])

    def test_verification_messages(self):
        """Test verification message utility function"""
        # Test unverified user
        message_unverified = get_verification_message(self.user_unverified)
        self.assertIn("verify", message_unverified.lower())
        
        # Test phone verified user
        message_phone = get_verification_message(self.user_phone_verified)
        self.assertIn("phone", message_phone.lower())
        self.assertIn("email", message_phone.lower())
        
        # Test email verified user
        message_email = get_verification_message(self.user_email_verified)
        self.assertIn("phone", message_email.lower())
        self.assertIn("email", message_email.lower())
        
        # Test fully verified user
        message_fully = get_verification_message(self.user_fully_verified)
        self.assertIn("fully verified", message_fully.lower()) 