import traceback
from postprensa.models import ControlCalidad
from reportlab.platypus import Image as RLImage

c = ControlCalidad.objects.filter(imagenes__isnull=False).last()
if c:
    img_obj = c.imagenes.first()
    path = img_obj.imagen.path
    print(f"Path is: {path}")
    try:
        RLImage(path)
        print("ReportLab loaded the image successfully!")
    except Exception as e:
        print("Error loading image in ReportLab:")
        traceback.print_exc()
else:
    print("No controls with images found.")
