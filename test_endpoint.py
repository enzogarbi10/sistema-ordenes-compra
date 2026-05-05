import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User

user, _ = User.objects.get_or_create(username='testadmin', is_superuser=True, is_staff=True)
client = Client()
client.force_login(user)

response = client.post('/calidad/api/buscar-orden/', json.dumps({'orden': 38839}), content_type='application/json')
print("Status:", response.status_code)
print("Content:", response.content.decode('utf-8'))
