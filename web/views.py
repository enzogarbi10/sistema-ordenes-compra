from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.conf import settings
from .models import CategoriaMuestra, CategoriaTecnologia, SectorCliente
import logging

logger = logging.getLogger(__name__)



def home(request):
    contacto_ok = request.GET.get('contacto')
    return render(request, 'web/home.html', {'contacto_ok': contacto_ok})


def contacto(request):
    if request.method == 'POST':
        nombre = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        mensaje = request.POST.get('message', '').strip()

        if nombre and email and mensaje:
            try:
                send_mail(
                    subject=f'Nueva consulta desde la web Melfa - {nombre}',
                    message=f'Nombre: {nombre}\nEmail: {email}\n\nMensaje:\n{mensaje}',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=['enzogarbi@agmelfa.com.ar'],
                    fail_silently=False,
                )
                return redirect('/?contacto=ok#contacto')
            except Exception as e:
                logger.error(f"Error enviando email de contacto: {type(e).__name__}: {e}")
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

