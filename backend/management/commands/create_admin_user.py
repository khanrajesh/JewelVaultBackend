"""Create admin user management command."""

from django.core.management.base import BaseCommand
# UserRepository moved/removed; refactor to use Django auth or custom logic
# from backend.api.v1.users.repositories import UserRepository


class Command(BaseCommand):
    help = 'Create an admin user'
    
    def add_arguments(self, parser):
        parser.add_argument('--email', type=str, required=True, help='Admin email')
        parser.add_argument('--name', type=str, required=True, help='Admin name')
        parser.add_argument('--phone', type=str, required=True, help='Admin phone')
    
    def handle(self, *args, **options):
        # repo = UserRepository()
        
        # TODO: Implement admin user creation logic (e.g., using Django User model or custom logic)
        self.stdout.write('Admin user creation not yet implemented')
            self.stdout.write(self.style.ERROR('Admin user already exists'))
            return
        
        user = repo.create_user(
            name=options['name'],
            email=options['email'],
            mobileNo=options['phone'],
            role='admin'
        )
        
        self.stdout.write(self.style.SUCCESS(f'Admin user created successfully: {user.userId}'))
