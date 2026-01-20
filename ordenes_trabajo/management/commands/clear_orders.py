import os
import shutil
from django.core.management.base import BaseCommand
from django.conf import settings
from ordenes_trabajo_trabajo.models import OrdenCompra

class Command(BaseCommand):
    help = 'Clears all orders and deletes uploaded images'

    def handle(self, *args, **kwargs):
        # 1. Delete all orders
        count, _ = OrdenCompra.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f'Successfully deleted {count} orders.'))

        # 2. Clear media/muestras directory
        muestras_dir = os.path.join(settings.MEDIA_ROOT, 'muestras')
        if os.path.exists(muestras_dir):
            # Remove all files in the directory but keep the directory itself
            for filename in os.listdir(muestras_dir):
                file_path = os.path.join(muestras_dir, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Failed to delete {file_path}. Reason: {e}'))
            
            self.stdout.write(self.style.SUCCESS('Successfully cleared media/muestras directory.'))
        else:
            self.stdout.write(self.style.WARNING('media/muestras directory does not exist.'))
