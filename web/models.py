from django.db import models

class CategoriaMuestra(models.Model):
    nombre_clave = models.CharField("ID Categoria (ej: vinos)", max_length=50, unique=True, help_text="Se usa para la URL y enlaces (sin espacios)")
    titulo = models.CharField("Título Principal", max_length=100)
    subtitulo = models.CharField("Subtítulo", max_length=100)
    descripcion = models.TextField("Descripción")
    imagen = models.ImageField("Imagen Muestra", upload_to='portfolio/muestras/')
    etiquetas = models.CharField("Etiquetas", max_length=255, help_text="Separadas por coma. Ej: Hot Stamping Oro, Relieve Alto")
    fondo_css = models.CharField("Fondo CSS (opcional)", max_length=255, blank=True, help_text="Ej: radial-gradient(circle at 70% 50%, #2a1111, #0a0a0a)")
    orden = models.IntegerField("Orden de aparición", default=0)

    class Meta:
        verbose_name = "Muestra de Etiqueta"
        verbose_name_plural = "Muestras de Etiquetas"
        ordering = ['orden']

    def __str__(self):
        return self.titulo

    def get_etiquetas_list(self):
        return [tag.strip() for tag in self.etiquetas.split(',') if tag.strip()]

class CategoriaTecnologia(models.Model):
    nombre_clave = models.CharField("ID Tecnologia (ej: impresion)", max_length=50, unique=True)
    titulo = models.CharField("Título Principal", max_length=100)
    subtitulo = models.CharField("Subtítulo", max_length=100)
    descripcion = models.TextField("Descripción")
    imagen = models.ImageField("Imagen Tecnología", upload_to='portfolio/tecnologia/')
    etiquetas = models.CharField("Etiquetas", max_length=255, help_text="Separadas por coma.")
    fondo_css = models.CharField("Fondo CSS (opcional)", max_length=255, blank=True)
    orden = models.IntegerField("Orden de aparición", default=0)

    class Meta:
        verbose_name = "Tecnología"
        verbose_name_plural = "Tecnologías"
        ordering = ['orden']

    def __str__(self):
        return self.titulo

    def get_etiquetas_list(self):
        return [tag.strip() for tag in self.etiquetas.split(',') if tag.strip()]

class SectorCliente(models.Model):
    nombre_clave = models.CharField("ID Sector (ej: bodegas)", max_length=50, unique=True)
    titulo = models.CharField("Título Principal", max_length=100)
    subtitulo = models.CharField("Subtítulo", max_length=100)
    descripcion = models.TextField("Descripción")
    imagen = models.ImageField("Imagen Sector", upload_to='portfolio/clientes/')
    iconos_clases = models.CharField("Clases de FontAwesome", max_length=255, blank=True, help_text="Separadas por coma. Ej: fa-solid fa-wine-glass")
    fondo_css = models.CharField("Fondo CSS (opcional)", max_length=255, blank=True)
    orden = models.IntegerField("Orden de aparición", default=0)

    class Meta:
        verbose_name = "Sector de Cliente"
        verbose_name_plural = "Sectores de Clientes"
        ordering = ['orden']

    def __str__(self):
        return self.titulo
        
    def get_iconos_list(self):
        if self.iconos_clases:
            return [icon.strip() for icon in self.iconos_clases.split(',') if icon.strip()]
        return []
