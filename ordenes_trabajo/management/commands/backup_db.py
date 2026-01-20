from django.core.management.base import BaseCommand
from django.core.mail import EmailMessage
from django.conf import settings
from datetime import datetime
import os

class Command(BaseCommand):
    help = 'Envía un backup de la base de datos por email'

    def handle(self, *args, **options):
        db_path = settings.DATABASES['default']['NAME']
        
        if not os.path.exists(db_path):
            self.stdout.write(self.style.ERROR(f'No se encontró la base de datos en: {db_path}'))
            return

        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M")
        subject = f'Backup Base de Datos - {timestamp}'
        body = f'Adjunto encontrarás el backup de la base de datos generado el {timestamp}.'
        
        try:
            email = EmailMessage(
                subject=subject,
                body=body,
                from_email=settings.EMAIL_HOST_USER,
                to=['enzogarbi@agmelfa.com.ar'],
            )
            
            # Adjuntar el archivo db.sqlite3
            with open(db_path, 'rb') as f:
                email.attach('db.sqlite3', f.read(), 'application/x-sqlite3')
            
            email.send()
            self.stdout.write(self.style.SUCCESS(f'Backup enviado correctamente a enzogarbi@agmelfa.com.ar'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error al enviar backup: {e}'))
