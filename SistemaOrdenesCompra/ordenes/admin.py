from django.contrib import admin
from .models import Cliente, OrdenCompra, ItemOrden

class ItemOrdenInline(admin.TabularInline):
    model = ItemOrden
    extra = 0

@admin.register(OrdenCompra)
class OrdenCompraAdmin(admin.ModelAdmin):
    list_display = ('numero', 'cliente', 'fecha_creacion')
    inlines = [ItemOrdenInline]

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
