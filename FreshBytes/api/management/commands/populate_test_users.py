from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db import transaction
import random
from faker import Faker

User = get_user_model()
fake = Faker()

class Command(BaseCommand):
    help = 'Populate the database with test customers for development/testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=50,
            help='Number of test customers to create (default: 50)'
        )
        parser.add_argument(
            '--password',
            type=str,
            default='testpass123',
            help='Password for all test users (default: testpass123)'
        )
        parser.add_argument(
            '--verified',
            action='store_true',
            help='Mark all users as verified (email and phone)'
        )
        parser.add_argument(
            '--terms-accepted',
            action='store_true',
            help='Mark all users as having accepted terms'
        )

    def handle(self, *args, **options):
        count = options['count']
        password = options['password']
        verified = options['verified']
        terms_accepted = options['terms_accepted']

        self.stdout.write(f'Creating {count} test customers...')

        # Ensure Customer group exists
        customer_group, created = Group.objects.get_or_create(name='Customer')
        if created:
            self.stdout.write(self.style.SUCCESS('Created Customer group'))
        else:
            self.stdout.write('Customer group already exists')

        # Philippine cities and provinces for realistic addresses
        philippine_cities = [
            ('Manila', 'Metro Manila'),
            ('Quezon City', 'Metro Manila'),
            ('Makati', 'Metro Manila'),
            ('Taguig', 'Metro Manila'),
            ('Pasig', 'Metro Manila'),
            ('Cebu City', 'Cebu'),
            ('Davao City', 'Davao del Sur'),
            ('Iloilo City', 'Iloilo'),
            ('Bacolod', 'Negros Occidental'),
            ('Baguio', 'Benguet'),
            ('Cagayan de Oro', 'Misamis Oriental'),
            ('Zamboanga City', 'Zamboanga del Sur'),
            ('Antipolo', 'Rizal'),
            ('Caloocan', 'Metro Manila'),
            ('Las Piñas', 'Metro Manila'),
        ]

        # Philippine barangays (neighborhoods)
        barangays = [
            'Barangay 1', 'Barangay 2', 'Barangay 3', 'Barangay 4', 'Barangay 5',
            'Barangay 6', 'Barangay 7', 'Barangay 8', 'Barangay 9', 'Barangay 10',
            'Barangay 11', 'Barangay 12', 'Barangay 13', 'Barangay 14', 'Barangay 15',
            'Barangay 16', 'Barangay 17', 'Barangay 18', 'Barangay 19', 'Barangay 20',
            'Barangay 21', 'Barangay 22', 'Barangay 23', 'Barangay 24', 'Barangay 25',
            'Barangay 26', 'Barangay 27', 'Barangay 28', 'Barangay 29', 'Barangay 30',
        ]

        # Philippine street names
        streets = [
            'Rizal Street', 'Bonifacio Avenue', 'Aguinaldo Street', 'Luna Street',
            'Mabini Street', 'Quezon Avenue', 'Osmeña Street', 'Roxas Boulevard',
            'Marcos Highway', 'Aurora Boulevard', 'EDSA', 'Commonwealth Avenue',
            'Katipunan Avenue', 'C5 Road', 'C6 Road', 'NLEX', 'SLEX', 'Skyway',
            'Gil Puyat Avenue', 'Ayala Avenue', 'Makati Avenue', 'Buendia Avenue',
            'Taft Avenue', 'España Boulevard', 'Lacson Avenue', 'Legarda Street',
            'Banawe Street', 'Quezon Boulevard', 'Araneta Avenue', 'E. Rodriguez Avenue',
        ]

        created_users = []
        
        with transaction.atomic():
            for i in range(count):
                # Generate realistic Filipino names
                first_name = fake.first_name()
                last_name = fake.last_name()
                user_name = f"{first_name.lower()}{last_name.lower()}{random.randint(100, 999)}"
                
                # Generate unique email
                email = f"{user_name}@test.com"
                
                # Check if email already exists
                while User.objects.filter(user_email=email).exists():
                    user_name = f"{first_name.lower()}{last_name.lower()}{random.randint(100, 999)}"
                    email = f"{user_name}@test.com"

                # Generate Philippine phone number
                phone_prefixes = ['0915', '0916', '0917', '0918', '0919', '0920', '0921', '0922', '0923', '0924', '0925', '0926', '0927', '0928', '0929', '0930', '0931', '0932', '0933', '0934', '0935', '0936', '0937', '0938', '0939', '0940', '0941', '0942', '0943', '0944', '0945', '0946', '0947', '0948', '0949', '0950', '0951', '0952', '0953', '0954', '0955', '0956', '0957', '0958', '0959', '0960', '0961', '0962', '0963', '0964', '0965', '0966', '0967', '0968', '0969', '0970', '0971', '0972', '0973', '0974', '0975', '0976', '0977', '0978', '0979', '0980', '0981', '0982', '0983', '0984', '0985', '0986', '0987', '0988', '0989', '0990', '0991', '0992', '0993', '0994', '0995', '0996', '0997', '0998', '0999']
                phone = f"{random.choice(phone_prefixes)}{random.randint(1000000, 9999999)}"

                # Generate Philippine address
                city, province = random.choice(philippine_cities)
                barangay = random.choice(barangays)
                street = random.choice(streets)
                street_number = random.randint(1, 999)
                zip_code = f"{random.randint(1000, 9999)}"

                # Create user
                user = User.objects.create_user(
                    user_email=email,
                    password=password,
                    user_name=user_name,
                    first_name=first_name,
                    last_name=last_name,
                    user_phone=phone,
                    street=f"{street_number} {street}",
                    barangay=barangay,
                    city=city,
                    province=province,
                    zip_code=zip_code,
                    role='customer',
                    is_active=True,
                    is_staff=False,
                    is_superuser=False,
                    is_deleted=False,
                    terms_accepted=terms_accepted,
                    phone_verified=verified,
                    email_verified=verified,
                )

                # Assign to Customer group
                user.groups.add(customer_group)
                created_users.append(user)

                # Progress indicator
                if (i + 1) % 10 == 0:
                    self.stdout.write(f'Created {i + 1}/{count} users...')

        self.stdout.write(self.style.SUCCESS(f'Successfully created {len(created_users)} test customers!'))
        
        # Display sample users
        self.stdout.write('\nSample test users created:')
        for i, user in enumerate(created_users[:5]):
            self.stdout.write(f'{i+1}. {user.first_name} {user.last_name} ({user.user_email})')
        
        if len(created_users) > 5:
            self.stdout.write(f'... and {len(created_users) - 5} more users')
        
        self.stdout.write(f'\nAll users have password: {password}')
        self.stdout.write('You can now test your API with these credentials!') 