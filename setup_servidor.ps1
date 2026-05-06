# ============================================================
#  setup_servidor.ps1
#  Script de instalacion automatica - Windows Server 2022
#  Ejecutar como Administrador en el servidor
# ============================================================

$ErrorActionPreference = "Stop"
$ProjectDir = $PSScriptRoot   # Directorio donde esta este script

Write-Host ""
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "   INSTALACION - Sistema Ordenes de Compra" -ForegroundColor Cyan
Write-Host "   Grafica Melfa" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""

# --- 1. Verificar Python ---
Write-Host "[1/7] Verificando Python..." -ForegroundColor Yellow
try {
    $pyVersion = python --version 2>&1
    Write-Host "      OK: $pyVersion" -ForegroundColor Green
} catch {
    Write-Host "      ERROR: Python no esta instalado." -ForegroundColor Red
    Write-Host "      Descargalo de: https://www.python.org/downloads/release/python-31200/" -ForegroundColor Red
    Write-Host "      Asegurate de tildar 'Add Python to PATH' durante la instalacion." -ForegroundColor Red
    Read-Host "      Presiona Enter para salir"
    exit 1
}

# --- 2. Crear entorno virtual ---
Write-Host ""
Write-Host "[2/7] Creando entorno virtual..." -ForegroundColor Yellow
if (Test-Path "$ProjectDir\venv") {
    Write-Host "      El entorno virtual ya existe, omitiendo creacion." -ForegroundColor DarkGray
} else {
    python -m venv "$ProjectDir\venv"
    Write-Host "      OK: Entorno virtual creado." -ForegroundColor Green
}

# --- 3. Instalar dependencias ---
Write-Host ""
Write-Host "[3/7] Instalando dependencias (puede tardar unos minutos)..." -ForegroundColor Yellow
& "$ProjectDir\venv\Scripts\pip.exe" install --upgrade pip --quiet
& "$ProjectDir\venv\Scripts\pip.exe" install -r "$ProjectDir\requirements.txt"
Write-Host "      OK: Dependencias instaladas." -ForegroundColor Green

# --- 4. Configurar .env ---
Write-Host ""
Write-Host "[4/7] Configurando variables de entorno (.env)..." -ForegroundColor Yellow

$envFile = "$ProjectDir\.env"

if (Test-Path $envFile) {
    $overwrite = Read-Host "      Ya existe un .env. Sobreescribir? (s/N)"
    if ($overwrite -ne "s" -and $overwrite -ne "S") {
        Write-Host "      Manteniendo .env existente." -ForegroundColor DarkGray
        goto SkipEnv
    }
}

Write-Host ""
Write-Host "      Completa los siguientes datos:" -ForegroundColor Cyan
Write-Host ""

# Generar SECRET_KEY automaticamente
$secretKey = & "$ProjectDir\venv\Scripts\python.exe" -c "import secrets; print(secrets.token_urlsafe(50))"

$ipServer = Read-Host "      IP o dominio del servidor (ej: 192.168.1.100)"
$adminUrl = Read-Host "      URL del panel admin - ingresa algo dificil de adivinar (ej: gestion-interna-melfa/)"
$cloudinaryUrl = "cloudinary://374757464132777:xsrt9ptRGJLYMTZb_XimFlOPIRs@dbsvdv4tg"
$sendgridKey = Read-Host "      API Key de SendGrid (Enter para omitir)"

$envContent = @"
# Generado por setup_servidor.ps1 el $(Get-Date -Format 'yyyy-MM-dd HH:mm')
SECRET_KEY=$secretKey
DEBUG=False
ALLOWED_HOSTS=$ipServer,localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=http://$ipServer,https://$ipServer
DATABASE_URL=
CLOUDINARY_URL=$cloudinaryUrl
SENDGRID_API_KEY=$sendgridKey
ADMIN_URL=$adminUrl
"@

Set-Content -Path $envFile -Value $envContent -Encoding UTF8
Write-Host "      OK: Archivo .env creado." -ForegroundColor Green

:SkipEnv

# --- 5. Crear carpeta de logs ---
Write-Host ""
Write-Host "[5/7] Creando carpeta de logs..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path "$ProjectDir\logs" | Out-Null
Write-Host "      OK: Carpeta logs/ lista." -ForegroundColor Green

# --- 6. Migraciones y archivos estaticos ---
Write-Host ""
Write-Host "[6/7] Aplicando migraciones y recolectando estaticos..." -ForegroundColor Yellow

$env:DJANGO_SETTINGS_MODULE = "core.settings"
Set-Location $ProjectDir

& "$ProjectDir\venv\Scripts\python.exe" manage.py migrate --no-input
Write-Host "      OK: Migraciones aplicadas." -ForegroundColor Green

& "$ProjectDir\venv\Scripts\python.exe" manage.py collectstatic --no-input
Write-Host "      OK: Archivos estaticos recolectados." -ForegroundColor Green

# --- 7. Instalar como servicio Windows (NSSM) ---
Write-Host ""
Write-Host "[7/7] Servicio de Windows..." -ForegroundColor Yellow

$nssmPath = "C:\Tools\nssm.exe"
if (Test-Path $nssmPath) {
    $installService = Read-Host "      NSSM encontrado. Instalar/actualizar servicio DjangoMelfa? (s/N)"
    if ($installService -eq "s" -or $installService -eq "S") {
        # Detener y eliminar servicio anterior si existe
        $existingService = Get-Service -Name "DjangoMelfa" -ErrorAction SilentlyContinue
        if ($existingService) {
            & $nssmPath stop DjangoMelfa
            & $nssmPath remove DjangoMelfa confirm
            Start-Sleep -Seconds 2
        }

        & $nssmPath install DjangoMelfa "$ProjectDir\venv\Scripts\python.exe"
        & $nssmPath set DjangoMelfa AppDirectory "$ProjectDir"
        & $nssmPath set DjangoMelfa AppParameters "serve.py"
        & $nssmPath set DjangoMelfa DisplayName "Django - Sistema Ordenes Melfa"
        & $nssmPath set DjangoMelfa Description "Servidor web del sistema de ordenes de compra"
        & $nssmPath set DjangoMelfa AppEnvironmentExtra "DJANGO_SETTINGS_MODULE=core.settings"
        & $nssmPath set DjangoMelfa Start SERVICE_AUTO_START
        & $nssmPath set DjangoMelfa AppStdout "$ProjectDir\logs\service_stdout.log"
        & $nssmPath set DjangoMelfa AppStderr "$ProjectDir\logs\service_stderr.log"
        & $nssmPath start DjangoMelfa

        Write-Host "      OK: Servicio DjangoMelfa instalado e iniciado." -ForegroundColor Green
    }
} else {
    Write-Host "      NSSM no encontrado en C:\Tools\nssm.exe" -ForegroundColor DarkYellow
    Write-Host "      Descargalo de https://nssm.cc/download y guardalo en C:\Tools\" -ForegroundColor DarkYellow
    Write-Host "      Luego volvé a ejecutar este script." -ForegroundColor DarkYellow
}

# --- Resultado final ---
Write-Host ""
Write-Host "========================================================" -ForegroundColor Green
Write-Host "   INSTALACION COMPLETADA" -ForegroundColor Green
Write-Host "========================================================" -ForegroundColor Green
Write-Host ""
Write-Host "   Para probar el servidor manualmente:" -ForegroundColor White
Write-Host "   cd $ProjectDir" -ForegroundColor Gray
Write-Host "   python serve.py" -ForegroundColor Gray
Write-Host ""
Write-Host "   Luego abri el navegador en: http://localhost:8000" -ForegroundColor White
Write-Host ""
Write-Host "   Para ver los logs del servicio:" -ForegroundColor White
Write-Host "   $ProjectDir\logs\" -ForegroundColor Gray
Write-Host ""
Read-Host "Presiona Enter para cerrar"
