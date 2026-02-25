import traceback
from postprensa.views import enviar_email_nuevo_control_bg
from postprensa.models import ControlCalidad

c = ControlCalidad.objects.last()
print(c)
try:
    enviar_email_nuevo_control_bg(c.id)
except Exception as e:
    traceback.print_exc()
