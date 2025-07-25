from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

class Command(BaseCommand):
    help = 'Ensure groups exist and assign users to groups based on their role field.'

    def handle(self, *args, **options):
        User = get_user_model()
        roles = ['Admin', 'Seller', 'Customer']
        for role in roles:
            group, created = Group.objects.get_or_create(name=role)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created group: {role}'))
            else:
                self.stdout.write(f'Group already exists: {role}')

        users = User.objects.all()
        for user in users:
            # Remove user from all target groups first
            for role in roles:
                group = Group.objects.get(name=role)
                user.groups.remove(group)
            # Assign user to group based on their role field
            user_role = getattr(user, 'role', None)
            if user_role:
                group_name = user_role.capitalize()
                if group_name in roles:
                    group = Group.objects.get(name=group_name)
                    user.groups.add(group)
                    self.stdout.write(self.style.SUCCESS(f'Assigned {user} to group {group_name}'))
        self.stdout.write(self.style.SUCCESS('Group setup and user assignment complete.')) 