
import os
import django
from django.urls import get_resolver
from django.conf import settings

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

resolver = get_resolver()
print("Registered Namespaces:")
for ns in resolver.namespace_dict:
    print(f"- {ns}")

print("\nURL Patterns:")
for pattern in resolver.url_patterns:
    print(pattern)
