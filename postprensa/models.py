from django.db import models
from ordenes_trabajo.models import OrdenCompra, Cliente
from django.utils import timezone


class Maquinista(models.Model):
    nombre = models.CharField("Nombre", max_length=100, unique=True)
    activo = models.BooleanField("Activo", default=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Maquinista"
        verbose_name_plural = "Maquinistas"
        ordering = ['nombre']


class OperarioInspeccion(models.Model):
    nombre = models.CharField("Nombre", max_length=100, unique=True)
    activo = models.BooleanField("Activo", default=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Operario de Inspección"
        verbose_name_plural = "Operarios de Inspección"
        ordering = ['nombre']


class TipoDefecto(models.Model):
    nombre = models.CharField("Nombre", max_length=100, unique=True)
    activo = models.BooleanField("Activo", default=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Tipo de Defecto"
        verbose_name_plural = "Tipos de Defecto"
        ordering = ['nombre']


class OpcionDefecto(models.Model):
    tipo_defecto = models.ForeignKey(
        TipoDefecto,
        on_delete=models.CASCADE,
        related_name='opciones',
        verbose_name="Tipo de Defecto",
    )
    nombre = models.CharField("Nombre", max_length=150)
    activo = models.BooleanField("Activo", default=True)

    def __str__(self):
        return f"{self.tipo_defecto.nombre} → {self.nombre}"

    class Meta:
        verbose_name = "Opción de Defecto"
        verbose_name_plural = "Opciones de Defecto"
        ordering = ['tipo_defecto', 'nombre']
        unique_together = ['tipo_defecto', 'nombre']


class ControlCalidad(models.Model):
    orden = models.CharField("N° Orden de Trabajo", max_length=50)
    fecha = models.DateTimeField(default=timezone.now)
    operario = models.ForeignKey(
        OperarioInspeccion,
        on_delete=models.PROTECT,
        verbose_name="Operario Inspección",
        null=True,
    )
    maquinista = models.ForeignKey(
        Maquinista,
        on_delete=models.PROTECT,
        verbose_name="Maquinista",
        null=True,
    )
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.PROTECT,
        verbose_name="Cliente",
        null=True,
        blank=True,
    )
    bobina = models.CharField("N° Bobina", max_length=100, blank=True)
    cantidad_descartada = models.PositiveIntegerField("Cantidad Descartada", default=0)
    
    # Defectos
    defectos = models.ManyToManyField(TipoDefecto, blank=True, verbose_name="Tipos de Defecto")
    opciones_defecto = models.ManyToManyField(OpcionDefecto, blank=True, verbose_name="Opciones de Defecto")
    
    detalle_defecto = models.TextField("Descripción del Defecto", blank=True)
    
    # Cierre
    llego_cantidad = models.BooleanField("¿Se llegó a la cantidad?", default=True)
    autorizo_envio = models.CharField("Autorizó Envío", max_length=100, blank=True)
    
    # No Conformidades
    TIPO_NC_CHOICES = [
        ('INTERNA', 'Interna'),
        ('EXTERNA', 'Externa'),
    ]
    SUBTIPO_NC_CHOICES = [
        ('RECLAMO', 'Reclamo'),
        ('RECHAZO', 'Rechazo'),
    ]
    no_conformidad = models.CharField("No Conformidad", max_length=10, choices=TIPO_NC_CHOICES, blank=True, null=True)
    tipo_no_conformidad = models.CharField("Tipo (Externa)", max_length=10, choices=SUBTIPO_NC_CHOICES, blank=True, null=True)
    nro_no_conformidad = models.CharField("N° referencial asociada", max_length=50, blank=True)

    observaciones = models.TextField("Observaciones Generales", blank=True)
    
    # Auditoría
    creado_por = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name="Creado por",
        related_name='controles_creados',
    )

    def __str__(self):
        return f"Control OT #{self.orden} - {self.fecha.strftime('%d/%m/%Y')}"

    class Meta:
        verbose_name = "Control de Calidad"
        verbose_name_plural = "Controles de Calidad"
        ordering = ['-fecha']


class ImagenControl(models.Model):
    control = models.ForeignKey(ControlCalidad, on_delete=models.CASCADE, related_name='imagenes')
    imagen = models.ImageField(upload_to='calidad/evidencias/')
    descripcion = models.CharField(max_length=200, blank=True)
    fecha_subida = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Imagen para {self.control}"


class NotificacionEmail(models.Model):
    email = models.EmailField("Correo Electrónico", unique=True)
    activo = models.BooleanField("Activo", default=True, help_text="Si está activo, recibirá los correos automáticos al registrar controles.")

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = "Notificación por Correo"
        verbose_name_plural = "Notificaciones por Correo"
        ordering = ['email']
