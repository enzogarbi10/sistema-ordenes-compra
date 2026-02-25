from django.contrib import admin
from .models import ControlCalidad, ImagenControl, Maquinista, OperarioInspeccion, TipoDefecto, OpcionDefecto, NotificacionEmail

@admin.register(NotificacionEmail)
class NotificacionEmailAdmin(admin.ModelAdmin):
    list_display = ('email', 'activo')
    list_filter = ('activo',)
    search_fields = ('email',)

class ImagenControlInline(admin.TabularInline):
    model = ImagenControl
    extra = 1

class OpcionDefectoInline(admin.TabularInline):
    model = OpcionDefecto
    extra = 1

@admin.register(ControlCalidad)
class ControlCalidadAdmin(admin.ModelAdmin):
    list_display = ('id', 'orden', 'fecha', 'operario', 'maquinista', 'autorizo_envio', 'creado_por')
    list_filter = ('fecha', 'operario', 'maquinista', 'defectos')
    search_fields = ('orden', 'operario__nombre', 'maquinista__nombre')
    filter_horizontal = ('defectos', 'opciones_defecto')
    inlines = [ImagenControlInline]

@admin.register(Maquinista)
class MaquinistaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'activo')
    list_filter = ('activo',)
    search_fields = ('nombre',)

@admin.register(OperarioInspeccion)
class OperarioInspeccionAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'activo')
    list_filter = ('activo',)
    search_fields = ('nombre',)

@admin.register(TipoDefecto)
class TipoDefectoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'activo')
    list_filter = ('activo',)
    search_fields = ('nombre',)
    inlines = [OpcionDefectoInline]

@admin.register(OpcionDefecto)
class OpcionDefectoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo_defecto', 'activo')
    list_filter = ('activo', 'tipo_defecto')
    search_fields = ('nombre',)
