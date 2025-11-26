from django.db import models

from django.contrib.auth.models import User

class Cliente(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    nombre = models.CharField(max_length=100)
    
    def __str__(self):
        return self.nombre

class OrdenCompra(models.Model):
    numero = models.IntegerField(unique=True, editable=False)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.numero:
            last_order = OrdenCompra.objects.all().order_by('numero').last()
            if last_order:
                self.numero = last_order.numero + 1
            else:
                self.numero = 1
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Orden N°{self.numero} - {self.cliente}"

class ItemOrden(models.Model):
    orden = models.ForeignKey(OrdenCompra, related_name='items', on_delete=models.CASCADE)
    marca = models.CharField(max_length=100)
    cantidad = models.IntegerField()
    # Medidas split
    ancho = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Ancho (cm)")
    alto = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Alto (cm)")
    # New fields
    FORMA_CHOICES = [
        ('rectangulo', 'Rectángulo'),
        ('cuadrado', 'Cuadrado'),
        ('trapecio_inv', 'Trapecio Inv.'),
        ('circulo', 'Círculo'),
        ('especial', 'Especial'),
        ('ovalo', 'Óvalo'),
        ('rombo', 'Rombo'),
        ('cuadrado_r_2_5', 'Cuadrado R 2,5'),
        ('rectangulo_r_2_5', 'Rectángulo R 2.5'),
    ]
    forma = models.CharField(max_length=50, choices=FORMA_CHOICES, default='rectangulo')
    papel = models.CharField(max_length=100)
    variedad = models.CharField(max_length=100)
    archivo_muestra = models.ImageField(upload_to='muestras/', blank=True, null=True, verbose_name="Muestra")
    
    # New requested fields
    grado_alcoholico = models.CharField(max_length=50, blank=True, null=True, verbose_name="Grado Alcohólico")
    codigo_cliente = models.CharField(max_length=50, blank=True, null=True, verbose_name="Código Cliente")
    anio = models.IntegerField(blank=True, null=True, verbose_name="Año")
    contenido_neto = models.CharField(max_length=50, blank=True, null=True, verbose_name="Contenido Neto")

    ELEMENTO_CHOICES = [
        ('etiqueta', 'Etiqueta'),
        ('contraetiqueta', 'Contraetiqueta'),
        ('cuello', 'Cuello'),
        ('bajo_etiqueta', 'Bajo etiqueta'),
        ('corbata', 'Corbata'),
        ('eticontra', 'Eticontra'),
        ('fajas', 'Fajas'),
        ('medalla', 'Medalla'),
        ('oblea', 'Oblea'),
        ('sticker', 'Sticker'),
        ('collarin', 'Collarín'),
    ]
    elemento = models.CharField(max_length=20, choices=ELEMENTO_CHOICES, default='etiqueta')
    
    # Finishes (Yes/No)
    serigrafia = models.BooleanField(default=False, verbose_name="Serigrafía")
    stamping = models.BooleanField(default=False, verbose_name="Stamping")
    relieve = models.BooleanField(default=False, verbose_name="Relieve")
    bajo_relieve = models.BooleanField(default=False, verbose_name="Bajo Relieve")
    gofrado = models.BooleanField(default=False, verbose_name="Gofrado")

    def __str__(self):
        return f"{self.cantidad} x {self.variedad} ({self.marca})"
