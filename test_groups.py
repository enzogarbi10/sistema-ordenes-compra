import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.template import Template, Context
from django.contrib.auth.models import User

# This simulates a request with a particular user
u = User.objects.last()
class MockRequest:
    def __init__(self, user):
        self.user = user

t = Template("{% load web_extras %}{{ request.user|has_group:'Calidad' }}")
c = Context({'request': MockRequest(u)})

print("Template render Output:", t.render(c))
