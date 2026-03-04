from django.shortcuts import render, redirect
from .models import CategoriaMuestra, CategoriaTecnologia, SectorCliente
import logging
import os
import json
import urllib.request
import urllib.error

logger = logging.getLogger(__name__)


def _enviar_email_sendgrid(nombre, email, mensaje):
    """Envía email via API HTTP de SendGrid (puerto 443, no bloqueado en PythonAnywhere)."""
    api_key = os.environ.get('SENDGRID_API_KEY', '')
    if not api_key:
        logger.error("SENDGRID_API_KEY no está configurada en las variables de entorno.")
        return False

    payload = {
        "personalizations": [
            {
                "to": [{"email": "enzogarbi@agmelfa.com.ar"}],
            }
        ],
        "from": {"email": "graficamelfa@gmail.com", "name": "Gráfica Melfa Web"},
        "subject": f"Nueva consulta desde la web Melfa - {nombre}",
        "content": [
            {
                "type": "text/plain",
                "value": f"Nombre: {nombre}\nEmail: {email}\n\nMensaje:\n{mensaje}"
            }
        ]
    }

    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(
        'https://api.sendgrid.com/v3/mail/send',
        data=data,
        headers={
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
        },
        method='POST'
    )

    try:
        with urllib.request.urlopen(req) as response:
            return response.status == 202
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8')
        logger.error(f"SendGrid API error {e.code}: {body}")
        return False
    except Exception as e:
        logger.error(f"Error inesperado SendGrid: {type(e).__name__}: {e}")
        return False


def home(request):
    contacto_ok = request.GET.get('contacto')
    return render(request, 'web/home.html', {'contacto_ok': contacto_ok})


def contacto(request):
    if request.method == 'POST':
        nombre = request.POST.get('name', '').strip()
        email  = request.POST.get('email', '').strip()
        mensaje = request.POST.get('message', '').strip()

        if nombre and email and mensaje:
            if _enviar_email_sendgrid(nombre, email, mensaje):
                return redirect('/?contacto=ok#contacto')
            else:
                return redirect('/?contacto=error#contacto')

    return redirect('/#contacto')


def muestras(request):
    categorias = CategoriaMuestra.objects.all()
    return render(request, 'web/muestras.html', {'categorias': categorias})


def tecnologia(request):
    tecnologias = CategoriaTecnologia.objects.all()
    return render(request, 'web/tecnologia.html', {'tecnologias': tecnologias})


def clientes(request):
    sectores = SectorCliente.objects.all()
    return render(request, 'web/clientes.html', {'sectores': sectores})

