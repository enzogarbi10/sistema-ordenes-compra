from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('contacto/', views.contacto, name='contacto_web'),
    path('muestras/', views.muestras, name='muestras'),
    path('tecnologia/', views.tecnologia, name='tecnologia'),
    path('clientes/', views.clientes, name='clientes'),
]
