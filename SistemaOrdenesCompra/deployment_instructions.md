# Guía de Despliegue en PythonAnywhere

Sigue estos pasos para poner tu aplicación en línea.

## 1. Subir el Proyecto
1.  Inicia sesión en tu cuenta de [PythonAnywhere](https://www.pythonanywhere.com/).
2.  Ve a la pestaña **Files**.
3.  En el directorio `/home/tu_usuario/`, usa el botón **"Upload a file"** para subir el archivo `SistemaOrdenesCompra.zip` que generamos.

## 2. Descomprimir y Configurar Entorno
1.  Abre una **Bash console** desde el Dashboard.
2.  Ejecuta los siguientes comandos (reemplaza `tu_usuario` con tu nombre de usuario real si es necesario, aunque `~` suele funcionar):

```bash
# Descomprimir
unzip SistemaOrdenesCompra.zip

# Crear entorno virtual
mkvirtualenv --python=/usr/bin/python3.10 mi_entorno
# (Nota: Si mkvirtualenv no funciona, usa: python3.10 -m venv mi_entorno && source mi_entorno/bin/activate)

# Instalar dependencias
pip install -r requirements.txt
```

## 3. Configurar la Web App
1.  Ve a la pestaña **Web**.
2.  Haz clic en **"Add a new web app"**.
3.  Elige **Manual configuration** (no elijas la opción de Django automática, ya que subimos nuestro propio código).
4.  Selecciona **Python 3.10** (o la versión que hayas usado para el entorno virtual).

### Configurar Virtualenv
En la sección **Virtualenv** de la pestaña Web:
-   Ingresa la ruta a tu entorno virtual: `/home/tu_usuario/.virtualenvs/mi_entorno` (o donde lo hayas creado).

### Configurar Código
En la sección **Code**:
-   **Source code:** `/home/tu_usuario/`
-   **Working directory:** `/home/tu_usuario/`

### Configurar WSGI
Haz clic en el enlace del archivo **WSGI configuration file** (ej. `/var/www/tu_usuario_pythonanywhere_com_wsgi.py`) y reemplaza TODO su contenido con esto:

```python
import os
import sys

# Ruta al proyecto
path = '/home/tu_usuario'
if path not in sys.path:
    sys.path.append(path)

# Configuración de Django
os.environ['DJANGO_SETTINGS_MODULE'] = 'gestion_ordenes.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```
*Asegúrate de cambiar `tu_usuario` por tu nombre de usuario real.*

## 4. Archivos Estáticos
En la sección **Static files**:
-   **URL:** `/static/`
-   **Directory:** `/home/tu_usuario/static/`

## 5. Base de Datos y Superusuario
Vuelve a la **Bash console** y ejecuta:

```bash
# Activar entorno (si no está activo)
workon mi_entorno 
# o: source mi_entorno/bin/activate

# Ir a la carpeta del proyecto
cd ~

# Migrar base de datos (asegura que las tablas existan)
python manage.py migrate

# Crear superusuario (para poder entrar al admin y gestionar usuarios)
python manage.py createsuperuser
```
Sigue las instrucciones para poner un usuario y contraseña.

## 6. Finalizar
1.  Ve a la pestaña **Web** nuevamente.
2.  Haz clic en el botón verde **Reload**.
3.  ¡Listo! Tu sitio debería estar accesible en `tu_usuario.pythonanywhere.com`.

---

---
**Nota sobre DEBUG:**
Actualmente el proyecto tiene `DEBUG = True`. Para producción, deberías cambiarlo a `False` en `gestion_ordenes/settings.py` y configurar `ALLOWED_HOSTS = ['tu_usuario.pythonanywhere.com']`. Puedes editar este archivo desde la pestaña **Files** de PythonAnywhere.

## 7. Blanquear Base de Datos e Imágenes
Si necesitas borrar TODAS las órdenes y las imágenes cargadas (por ejemplo, para limpiar datos de prueba), hemos creado un comando especial para esto.

**¡ADVERTENCIA! Esto borrará permanentemente todas las órdenes y las imágenes asociadas.**

Para ejecutarlo:
1.  Abre una **Bash console**.
2.  Asegúrate de estar en tu entorno virtual (`workon mi_entorno`).
3.  Ejecuta:
    ```bash
    python manage.py clear_orders
    ```
