from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Create a superuser with a mobile number'

    def handle(self, *args, **options):
        if not User.objects.filter(is_superuser=True).exists():
            mobile = input('Enter mobile number: ')
            username = input('Enter username: ')
            password = input('Enter password: ')
            
            User.objects.create_superuser(
                username=username,
                mobile=mobile,
                password=password,
                is_active=True
            )
            
            self.stdout.write(self.style.SUCCESS('Superuser created successfully'))
        else:
            self.stdout.write(self.style.WARNING('Superuser already exists'))