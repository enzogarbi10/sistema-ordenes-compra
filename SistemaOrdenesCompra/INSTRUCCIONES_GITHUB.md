# Guía para subir tu proyecto a GitHub

Parece que **Git no está instalado** o no está configurado en tu sistema. Sigue estos pasos para subir tu proyecto.

## 1. Instalar Git
1. Descarga Git desde [git-scm.com](https://git-scm.com/download/win).
2. Instálalo aceptando las opciones por defecto.
3. Abre una nueva terminal (PowerShell o CMD) para verificar que se instaló escribiendo:
   ```powershell
   git --version
   ```

## 2. Configurar Git (Solo la primera vez)
Ejecuta estos comandos en la terminal con tu nombre y correo:
```powershell
git config --global user.name "Tu Nombre"
git config --global user.email "tu@email.com"
```

## 3. Inicializar el Repositorio
Abre la terminal en la carpeta de tu proyecto (`C:\Users\ENZO\OneDrive\Desktop\PROYECTO WEB\SistemaOrdenesCompra`) y ejecuta:

```powershell
# 1. Inicializar git
git init

# 2. Agregar todos los archivos (ya creé el .gitignore para excluir archivos innecesarios)
git add .

# 3. Guardar los cambios (commit)
git commit -m "Primer commit: Sistema de Ordenes de Compra"
```

## 4. Subir a GitHub
1. Ve a [GitHub.com](https://github.com) e inicia sesión.
2. Crea un **New Repository** (Nuevo Repositorio).
3. Ponle un nombre (ej: `sistema-ordenes-compra`) y dale a **Create repository**.
4. Copia los comandos que aparecen bajo la sección **"…or push an existing repository from the command line"**. Deberían verse así:

```powershell
git remote add origin https://github.com/TU_USUARIO/sistema-ordenes-compra.git
git branch -M main
git push -u origin main
```
5. Pégalos en tu terminal y presiona Enter.

¡Listo! Tu proyecto estará en GitHub.
