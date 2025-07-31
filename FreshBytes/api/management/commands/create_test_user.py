from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

User = get_user_model()

class Command(BaseCommand):
    help = 'Create a single test user with specified details'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            default='test@example.com',
            help='Email for the test user'
        )
        parser.add_argument(
            '--password',
            type=str,
            default='testpass123',
            help='Password for the test user'
        )
        parser.add_argument(
            '--first-name',
            type=str,
            default='Test',
            help='First name for the test user'
        )
        parser.add_argument(
            '--last-name',
            type=str,
            default='User',
            help='Last name for the test user'
        )
        parser.add_argument(
            '--phone',
            type=str,
            default='09171234567',
            help='Phone number for the test user'
        )
        parser.add_argument(
            '--role',
            type=str,
            choices=['customer', 'seller', 'admin'],
            default='customer',
            help='Role for the test user'
        )
        parser.add_argument(
            '--verified',
            action='store_true',
            help='Mark user as verified (email and phone)'
        )
        parser.add_argument(
            '--terms-accepted',
            action='store_true',
            help='Mark user as having accepted terms'
        )

    def handle(self, *args, **options):
        email = options['email']
        password = options['password']
        first_name = options['first_name']
        last_name = options['last_name']
        phone = options['phone']
        role = options['role']
        verified = options['verified']
        terms_accepted = options['terms_accepted']

        # Check if user already exists
        if User.objects.filter(user_email=email).exists():
            self.stdout.write(
                self.style.WARNING(f'User with email {email} already exists!')
            )
            return

        # Generate username
        user_name = f"{first_name.lower()}{last_name.lower()}"

        # Create user
        user = User.objects.create_user(
            user_email=email,
            password=password,
            user_name=user_name,
            first_name=first_name,
            last_name=last_name,
            user_phone=phone,
            street='123 Test Street',
            barangay='Test Barangay',
            city='Test City',
            province='Test Province',
            zip_code='1234',
            role=role,
            is_active=True,
            is_staff=(role == 'admin'),
            is_superuser=(role == 'admin'),
            is_deleted=False,
            terms_accepted=terms_accepted,
            phone_verified=verified,
            email_verified=verified,
        )

        # Assign to appropriate group
        group_name = role.capitalize()
        group, created = Group.objects.get_or_create(name=group_name)
        user.groups.add(group)

        if created:
            self.stdout.write(self.style.SUCCESS(f'Created group: {group_name}'))

        self.stdout.write(self.style.SUCCESS(f'Successfully created test user!'))
        self.stdout.write(f'Email: {email}')
        self.stdout.write(f'Password: {password}')
        self.stdout.write(f'Role: {role}')
        self.stdout.write(f'Name: {first_name} {last_name}')
        self.stdout.write(f'Phone: {phone}')
        self.stdout.write(f'Verified: {verified}')
        self.stdout.write(f'Terms Accepted: {terms_accepted}') 