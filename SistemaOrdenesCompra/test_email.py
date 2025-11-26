import os
import django
from django.core.mail import send_mail
from django.conf import settings
import traceback

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_ordenes.settings')
django.setup()

print("Testing email configuration...")
print(f"Host: {settings.EMAIL_HOST}")
print(f"Port: {settings.EMAIL_PORT}")
print(f"User: {settings.EMAIL_HOST_USER}")
print(f"Backend: {settings.EMAIL_BACKEND}")

from django.core.mail import EmailMessage

# ... (imports)

try:
    email = EmailMessage(
        'Test Email with Attachment',
        'This is a test email with a dummy PDF attachment.',
        settings.EMAIL_HOST_USER,
        ['ventas@agmelfa.com.ar'],
    )
    # Create a dummy PDF content (just text for testing)
    email.attach('test.pdf', b'%PDF-1.4\n%EOF', 'application/pdf')
    email.send()
    print("Email with attachment sent successfully!")
except Exception as e:
    print("\nFAILED to send email.")
    print(f"Error: {e}")
    print("\nTraceback:")
    traceback.print_exc()
