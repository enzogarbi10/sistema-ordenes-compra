
import os
import sys
import django
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

def setup_groups():
    # 1. Create Groups
    grupo_ordenes, created = Group.objects.get_or_create(name='Ordenes')
    grupo_calidad, created = Group.objects.get_or_create(name='Calidad')
    
    print(f"Groups 'Ordenes' and 'Calidad' ready.")

    # 2. Assign Permissions (Optional but good practice)
    # Get content types
    # ct_orden = ContentType.objects.get(app_label='ordenes_trabajo', model='ordencompra')
    # ct_control = ContentType.objects.get(app_label='postprensa', model='controlcalidad')
    
    # Ensure existing users are handled (for dev purposes, maybe add admin to both?)
    from django.contrib.auth.models import User
    try:
        admin_user = User.objects.get(username='admin')
        admin_user.groups.add(grupo_ordenes, grupo_calidad)
        print("Added 'admin' to both groups for testing.")
    except User.DoesNotExist:
        pass

if __name__ == '__main__':
    setup_groups()
