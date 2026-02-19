
import os
import sys
import django
from django.urls import get_resolver

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

def print_urls(patterns, prefix=''):
    for pattern in patterns:
        if hasattr(pattern, 'url_patterns'):
            # It's a resolver (include)
            # Try to get the regex pattern
            p = getattr(pattern.pattern, 'regex', None)
            regex = p.pattern if p else str(pattern.pattern)
            print_urls(pattern.url_patterns, prefix + regex)
        elif hasattr(pattern, 'name'):
            # It's a view
            p = getattr(pattern.pattern, 'regex', None)
            regex = p.pattern if p else str(pattern.pattern)
            print(f"Name: {pattern.name or 'None'} | Full Path: {prefix}{regex}")

resolver = get_resolver()
print("Scanning all URL patterns...")
print_urls(resolver.url_patterns)
