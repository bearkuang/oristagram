from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from instaapp.models import CustomUser

class Command(BaseCommand):
    help = 'Creates dummy users'

    def handle(self, *args, **options):
        dummy_users = [
            {
                'username': 'aespa_official',
                'email': 'aespa@aespa.com',
                'password': make_password('testpassword'),
                'name': 'aespa 에스파',
                'bio': 'aespa 에스파 Japan Debut Single〖Hot Mess〗',
                'birth_date': '1990-01-01',
            },
            {
                'username': 'newjeans.updates',
                'email': 'newjeans@newjeans.com',
                'password': make_password('testpassword'),
                'name': 'NewJeans 뉴진스 fanpage/updates 💕💕',
                'bio': 'newjeans_official',
                'birth_date': '1991-02-02',
            },
            {
                'username': 'catneko',
                'email': 'catneko@catneko.com',
                'password': make_password('testpassword'),
                'name': 'catneko',
                'bio': 'I take a photos of island cats',
                'birth_date': '1990-01-01',
            },
            {
                'username': 'ya_zi',
                'email': 'ya_zi@yazi.com',
                'password': make_password('testpassword'),
                'name': 'ya_zi',
                'bio': '主要拍鸭子的照片',
                'birth_date': '1991-02-02',
            },
            {
                'username': 'ori',
                'email': 'ori178205@gmail.com',
                'password': make_password('testpassword'),
                'name': '오리',
                'bio': 'Dori 쇼핑몰 CEO',
                'birth_date': '1990-01-01',
            },
        ]

        for user_data in dummy_users:
            username = user_data['username']
            if not CustomUser.objects.filter(username=username).exists():
                CustomUser.objects.create(**user_data)
                self.stdout.write(self.style.SUCCESS(f'Successfully created user {username}'))
            else:
                self.stdout.write(self.style.WARNING(f'User {username} already exists. Skipping.'))