from django.shortcuts import render
from .models import CategoriaMuestra, CategoriaTecnologia, SectorCliente

def home(request):
    return render(request, 'web/home.html', {})

def muestras(request):
    categorias = CategoriaMuestra.objects.all()
    return render(request, 'web/muestras.html', {'categorias': categorias})

def tecnologia(request):
    tecnologias = CategoriaTecnologia.objects.all()
    return render(request, 'web/tecnologia.html', {'tecnologias': tecnologias})

def clientes(request):
    sectores = SectorCliente.objects.all()
    return render(request, 'web/clientes.html', {'sectores': sectores})
