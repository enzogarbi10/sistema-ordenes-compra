import os
import django
from django.core.files.base import ContentFile
import urllib.request

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from web.models import CategoriaMuestra, CategoriaTecnologia, SectorCliente

def download_image(url, filename):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            return ContentFile(response.read(), name=filename)
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return None

# Muestras
muestras_data = [
    {
        'nombre_clave': 'vinos', 'titulo': 'Línea Vinos<br>& Bodegas', 'subtitulo': 'Premium Design',
        'descripcion': 'Elegancia y tradición en cada detalle. Utilizamos papeles texturados resistentes a la humedad, con acabados en hot stamping y relieves de alta precisión que elevan la percepción de su marca.',
        'etiquetas': 'Hot Stamping Oro, Relieve Alto, Papel Texturado, Barniz Sectorizado',
        'fondo_css': 'radial-gradient(circle at 70% 50%, #2a1111, #0a0a0a)',
        'img_url': 'https://images.unsplash.com/photo-1584916201218-f4242ceb4809?q=80&w=800&auto=format&fit=crop',
        'img_name': 'vinos.jpg'
    },
    {
        'nombre_clave': 'cosmetica', 'titulo': 'Belleza y<br>Cosmética', 'subtitulo': 'Estética Refinada',
        'descripcion': 'Atención impecable al mínimo detalle. Materiales sintéticos ultraclaros (no-label look) y acabados perlados que garantizan durabilidad frente a aceites y roce, manteniendo una imagen pulcra.',
        'etiquetas': 'No-label Look, Cold Stamping, BOPP Transparente, Plastificado Mate',
        'fondo_css': 'radial-gradient(circle at 30% 50%, #1c2321, #0a0a0a)',
        'img_url': 'https://images.unsplash.com/photo-1620916566398-39f1143ab7be?q=80&w=800&auto=format&fit=crop',
        'img_name': 'cosmetica.jpg'
    },
    {
        'nombre_clave': 'alimentos', 'titulo': 'Alimentos<br>Gourmet', 'subtitulo': 'Calidad Alimentaria',
        'descripcion': 'Colores vibrantes y máxima adherencia. Cuidamos que sus productos destaquen en la góndola mediante troqueles personalizados y tintas de alta pigmentación resistentes al frío y humedad.',
        'etiquetas': 'Troquelado Especial, Colores Pantone, Barniz Brillante, Adhesivo Frigorífico',
        'fondo_css': 'radial-gradient(circle at 70% 50%, #2e2417, #0a0a0a)',
        'img_url': 'https://images.unsplash.com/photo-1587049352847-4d4b124054da?q=80&w=800&auto=format&fit=crop',
        'img_name': 'alimentos.jpg'
    },
    {
        'nombre_clave': 'industrial', 'titulo': 'Industrial y<br>Bebidas Craft', 'subtitulo': 'Alta Resistencia',
        'descripcion': 'Desarrollos técnicos diseñados para soportar condiciones extremas o destacar en mercados dinámicos. Desde químicas hasta cervezas artesanales, aportamos soluciones robustas y creativas.',
        'etiquetas': 'Sintético Metalizado, Tintas UV, Barniz Mate, Antirrayaduras',
        'fondo_css': 'radial-gradient(circle at 30% 50%, #111a22, #0a0a0a)',
        'img_url': 'https://images.unsplash.com/photo-1614315585090-fb00561578e3?q=80&w=800&auto=format&fit=crop',
        'img_name': 'industrial.jpg'
    }
]

for i, data in enumerate(muestras_data):
    if not CategoriaMuestra.objects.filter(nombre_clave=data['nombre_clave']).exists():
        obj = CategoriaMuestra(
            nombre_clave=data['nombre_clave'], titulo=data['titulo'], subtitulo=data['subtitulo'],
            descripcion=data['descripcion'], etiquetas=data['etiquetas'], fondo_css=data['fondo_css'], orden=i
        )
        img = download_image(data['img_url'], data['img_name'])
        if img:
            obj.imagen.save(data['img_name'], img, save=False)
        obj.save()

# Tecnologia
tec_data = [
    {
        'nombre_clave': 'impresion', 'titulo': 'Impresión<br>Flexográfica', 'subtitulo': 'Precisión y Velocidad',
        'descripcion': 'Utilizamos prensas modulares de tambor central y banda angosta que garantizan un registro perfecto del color en altas velocidades, logrando definiciones fotográficas sobre cualquier sustrato.',
        'etiquetas': 'Hasta 10 Colores, Registro Automático, Tintas UV / Base Agua',
        'fondo_css': 'radial-gradient(circle at 70% 50%, #151515, #000000)',
        'img_url': 'https://images.unsplash.com/photo-1579848520845-ebd95cccd7b6?q=80&w=900&auto=format&fit=crop',
        'img_name': 'impresion.jpg'
    },
    {
        'nombre_clave': 'acabados', 'titulo': 'Acabados<br>Especiales', 'subtitulo': 'Diseño Premium',
        'descripcion': 'Módulos integrados en línea para estampar foils metálicos y aplicar relieves escultóricos sin perder velocidad y con un calce milimétrico, elevando drásticamente el valor percibido del producto.',
        'etiquetas': 'Hot / Cold Stamping, Relieve Seco, Barniz Cast&Cure',
        'fondo_css': 'radial-gradient(circle at 30% 50%, #1a1a1a, #050505)',
        'img_url': 'https://images.unsplash.com/photo-1618349271630-f2010bd74737?q=80&w=900&auto=format&fit=crop',
        'img_name': 'acabados.jpg'
    },
    {
        'nombre_clave': 'serigrafia', 'titulo': 'Serigrafía<br>Rotativa', 'subtitulo': 'Volumen y Textura',
        'descripcion': 'Incoporamos cuerpos de serigrafía en nuestras líneas para dar un depósito de tinta superior. Logre efectos táctiles, braille, y barnices de alto espesor que capturan la atención del consumidor.',
        'etiquetas': 'Barniz Volumen, Tintas Opacas, Acabado Táctil',
        'fondo_css': 'radial-gradient(circle at 70% 50%, #111111, #000000)',
        'img_url': 'https://images.unsplash.com/photo-1541604085465-926fb9dcf21d?q=80&w=900&auto=format&fit=crop',
        'img_name': 'serigrafia.jpg'
    },
    {
        'nombre_clave': 'inspeccion', 'titulo': 'Cámaras de<br>Inspección Digital', 'subtitulo': 'Control de Calidad 100%',
        'descripcion': 'Las rebobinadoras están equipadas con sistemas de visión artificial que escanean metro a metro la producción, descartando automáticamente cualquier mínima imperfección garantizando una entrega inmaculada.',
        'etiquetas': 'Inspección 100%, Control Tonal, Visión Artificial',
        'fondo_css': 'radial-gradient(circle at 30% 50%, #0a0a0a, #000000)',
        'img_url': 'https://images.unsplash.com/photo-1531297172864-45dc60645900?q=80&w=900&auto=format&fit=crop',
        'img_name': 'inspeccion.jpg'
    }
]

for i, data in enumerate(tec_data):
    if not CategoriaTecnologia.objects.filter(nombre_clave=data['nombre_clave']).exists():
        obj = CategoriaTecnologia(
            nombre_clave=data['nombre_clave'], titulo=data['titulo'], subtitulo=data['subtitulo'],
            descripcion=data['descripcion'], etiquetas=data['etiquetas'], fondo_css=data['fondo_css'], orden=i
        )
        img = download_image(data['img_url'], data['img_name'])
        if img:
            obj.imagen.save(data['img_name'], img, save=False)
        obj.save()


# Clientes
cli_data = [
    {
        'nombre_clave': 'bodegas', 'titulo': 'Bodegas<br>Premium', 'subtitulo': 'Sector Vitivinícola',
        'descripcion': 'Vestimos a los exponentes más exclusivos del vino local e internacional. Logramos transmitir el carácter orgánico del terruño en etiquetas con acabados majestuosos, respaldando el honor de la bodega.',
        'iconos_clases': 'fa-solid fa-wine-glass, fa-brands fa-envira, fa-solid fa-medal',
        'fondo_css': 'radial-gradient(circle at 70% 50%, #1e1111, #050505)',
        'img_url': 'https://images.unsplash.com/photo-1590740618015-ab1b9bfbc7e0?q=80&w=900&auto=format&fit=crop',
        'img_name': 'bodegas.jpg'
    },
    {
        'nombre_clave': 'cosmetica', 'titulo': 'Cuidado<br>Personal', 'subtitulo': 'Salud y Belleza',
        'descripcion': 'Laboratorios de cosmética de primeras marcas depositan en nosotros la delicada tarea de comunicar belleza, pureza y pulcritud a través de adhesivos técnicos ultra-cristalinos.',
        'iconos_clases': 'fa-solid fa-spa, fa-solid fa-leaf, fa-solid fa-spray-can-sparkles',
        'fondo_css': 'radial-gradient(circle at 30% 50%, #17111e, #050505)',
        'img_url': 'https://images.unsplash.com/photo-1614806687038-1647895e3dd9?q=80&w=900&auto=format&fit=crop',
        'img_name': 'cli_cosmetica.jpg'
    },
    {
        'nombre_clave': 'alimentos', 'titulo': 'Alimentos y<br>Bebidas', 'subtitulo': 'Consumo Masivo',
        'descripcion': 'Empresas de consumo masivo requieren logísticas dinámicas y calidades estandarizadas sin fisuras. Abastecemos de forma veloz para no frenar sus cadenas de producción alimenticias.',
        'iconos_clases': 'fa-solid fa-utensils, fa-solid fa-burger, fa-solid fa-cookie',
        'fondo_css': 'radial-gradient(circle at 70% 50%, #201a0f, #050505)',
        'img_url': 'https://images.unsplash.com/photo-1542838132-92c53300491e?q=80&w=900&auto=format&fit=crop',
        'img_name': 'cli_alimentos.jpg'
    },
    {
        'nombre_clave': 'industria', 'titulo': 'Industria y<br>Logística', 'subtitulo': 'Química y Agro',
        'descripcion': 'Fabricantes de insumos químicos o del agro, donde la legibilidad a lo largo del tiempo y frente a la erosión es un asunto de suma importancia y seguridad técnica.',
        'iconos_clases': 'fa-solid fa-flask, fa-solid fa-tractor, fa-solid fa-industry',
        'fondo_css': 'radial-gradient(circle at 30% 50%, #0c1a25, #000000)',
        'img_url': 'https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?q=80&w=900&auto=format&fit=crop',
        'img_name': 'cli_industria.jpg'
    }
]

for i, data in enumerate(cli_data):
    if not SectorCliente.objects.filter(nombre_clave=data['nombre_clave']).exists():
        obj = SectorCliente(
            nombre_clave=data['nombre_clave'], titulo=data['titulo'], subtitulo=data['subtitulo'],
            descripcion=data['descripcion'], iconos_clases=data['iconos_clases'], fondo_css=data['fondo_css'], orden=i
        )
        img = download_image(data['img_url'], data['img_name'])
        if img:
            obj.imagen.save(data['img_name'], img, save=False)
        obj.save()

print("Datos poblados exitosamente.")
