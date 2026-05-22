import os
import sys
import django

# Agregar el directorio del proyecto al path
project_path = r"C:\Users\ENZO\Desktop\PROYECTO WEB\sistema-ordenes-compra"
if project_path not in sys.path:
    sys.path.insert(0, project_path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

print("=" * 60)
print("   DIAGNOSTICO DE CONFIGURACION DE CORREO (SENDGRID)")
print("=" * 60)

try:
    django.setup()
    print("[OK] Django se inicializo correctamente.")
except Exception as e:
    print(f"[ERROR] Error al inicializar Django: {e}")
    sys.exit(1)

from django.conf import settings
from django.core.mail import send_mail

# 1. Verificar variables de entorno
api_key = os.environ.get('SENDGRID_API_KEY', '')
print("\n[1] Verificando Variables de Entorno:")
if not api_key:
    print("  [ERROR] SENDGRID_API_KEY: NO DEFINIDA o VACIA.")
    print("    -> Django no podra autenticarse con SendGrid.")
else:
    masked_key = api_key[:6] + "..." + api_key[-4:] if len(api_key) > 10 else "Muy corta"
    print(f"  [OK] SENDGRID_API_KEY: Encontrada ({masked_key})")

print(f"  * EMAIL_HOST: {settings.EMAIL_HOST}")
print(f"  * EMAIL_PORT: {settings.EMAIL_PORT}")
print(f"  * EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
print(f"  * EMAIL_USE_SSL: {settings.EMAIL_USE_SSL}")
print(f"  * EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
print(f"  * DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")

# 2. Intentar una prueba de conexión SMTP y envío real
print("\n[2] Probando envio de correo de prueba...")
destinatarios = [settings.DEFAULT_FROM_EMAIL] # Enviar un correo a sí mismo
print(f"  * Enviando de: {settings.DEFAULT_FROM_EMAIL}")
print(f"  * Enviando a: {destinatarios}")

try:
    sent = send_mail(
        subject="Prueba de Diagnostico - Sistema de Ordenes Melfa",
        message="Este es un correo de prueba automatico para diagnosticar la conexion con SendGrid.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=destinatarios,
        fail_silently=False,
    )
    if sent:
        print("\n=======================================================")
        print(" EXITOSO! El correo se envio correctamente.")
        print("=======================================================")
    else:
        print("\n[ERROR] El envio no arrojo error pero retorno 0 correos enviados.")
except Exception as e:
    print("\n[ERROR] ERROR AL ENVIAR EL CORREO:")
    import traceback
    traceback.print_exc()
    print("\n=======================================================")
    print(" RECOMENDACIONES:")
    print("=======================================================")
    if "550" in str(e) or "Unauthenticated senders not allowed" in str(e):
        print(" -> ERROR DE AUTENTICACION CON SENDGRID (550).")
        print("    La API Key de SendGrid esta vacia, es invalida o no se cargo.")
        print("    SOLUCION:")
        print("    1. Abre el archivo '.env' en la carpeta del proyecto en el servidor:")
        print("       C:\\Users\\ENZO\\Desktop\\PROYECTO WEB\\sistema-ordenes-compra\\.env")
        print("    2. Asegurate de agregar tu API Key de SendGrid real:")
        print("       SENDGRID_API_KEY=SG.xxxxxxxxxxxxxxxxxxxxxxxx")
        print("    3. Guarda el archivo y reinicia el servicio 'DjangoMelfa' en PowerShell:")
        print("       Restart-Service DjangoMelfa")
    elif "ConnectionRefusedError" in str(e) or "Timeout" in str(e):
        print(" -> ERROR DE CONEXION / CORTAFUEGOS.")
        print("    El servidor de produccion no puede conectar con 'smtp.sendgrid.net' en el puerto 587.")
        print("    1. Verifica que tu cortafuegos (Firewall) en Windows Server no este bloqueando")
        print("       las conexiones salientes al puerto 587.")
    else:
        print("    Verifica que la cuenta 'graficamelfa@gmail.com' este autorizada en SendGrid")
        print("    y que la API Key posea los permisos necesarios de envio.")
print("=" * 60)
