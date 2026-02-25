from django.contrib import admin
from .models import CategoriaMuestra, CategoriaTecnologia, SectorCliente

@admin.register(CategoriaMuestra)
class CategoriaMuestraAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'nombre_clave', 'orden')
    search_fields = ('titulo', 'nombre_clave')
    ordering = ('orden',)

@admin.register(CategoriaTecnologia)
class CategoriaTecnologiaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'nombre_clave', 'orden')
    search_fields = ('titulo', 'nombre_clave')
    ordering = ('orden',)

@admin.register(SectorCliente)
class SectorClienteAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'nombre_clave', 'orden')
    search_fields = ('titulo', 'nombre_clave')
    ordering = ('orden',)
