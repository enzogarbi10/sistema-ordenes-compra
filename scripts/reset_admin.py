
import os
import sys
import django

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User

try:
    user = User.objects.get(username='admin')
    user.set_password('admin123')
    user.save()
    print("SUCCESS: Password for 'admin' set to 'admin123'")
except User.DoesNotExist:
    print("ERROR: User 'admin' does not exist. Creating it...")
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print("SUCCESS: User 'admin' created with password 'admin123'")
