import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_ordenes.settings')
django.setup()

from django.contrib.auth.models import User

def setup_user(username, password):
    try:
        user = User.objects.get(username=username)
        print(f"Updating user: {username}")
    except User.DoesNotExist:
        user = User(username=username)
        print(f"Creating user: {username}")
    
    user.set_password(password)
    user.is_staff = True
    user.is_superuser = False
    user.save()
    print(f"User {username} configured successfully.")

if __name__ == '__main__':
    setup_user('jorge', 'Melfa2025')
    setup_user('cristian', 'Melfa2026')
