
import os
import sys
import django
from django.db import connection

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

with connection.cursor() as cursor:
    # Disable foreign key checks to avoid issues dropping tables
    cursor.execute("PRAGMA foreign_keys = OFF;")
    
    # Drop tables if they exist
    tables = ['postprensa_imagencontrol', 'postprensa_controlcalidad']
    for table in tables:
        try:
            cursor.execute(f"DROP TABLE IF EXISTS {table};")
            print(f"Dropped table {table}")
        except Exception as e:
            print(f"Error dropping {table}: {e}")
            
    # Also clear django_migrations record for postprensa
    try:
        cursor.execute("DELETE FROM django_migrations WHERE app = 'postprensa';")
        print("Cleared migration history for postprensa")
    except Exception as e:
        print(f"Error clearing migration history: {e}")

print("Reset complete.")
