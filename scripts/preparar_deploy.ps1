$sourceDir = "c:\Users\ENZO\OneDrive\Desktop\PROYECTO WEB\SistemaOrdenesCompra"
$desktopDir = "c:\Users\ENZO\OneDrive\Desktop"
$tempDir = Join-Path $desktopDir "Deploy_Temp"
$zipFile = Join-Path $desktopDir "SistemaOrdenes_Deploy.zip"

# Clean up previous runs
if (Test-Path $tempDir) { Remove-Item -Recurse -Force $tempDir }
if (Test-Path $zipFile) { Remove-Item -Force $zipFile }

# Create temp directory
New-Item -ItemType Directory -Path $tempDir | Out-Null

# Copy files
Write-Host "Copiando archivos..."
Copy-Item -Path "$sourceDir\manage.py" -Destination $tempDir
Copy-Item -Path "$sourceDir\db.sqlite3" -Destination $tempDir
Copy-Item -Path "$sourceDir\requirements.txt" -Destination $tempDir

# Copy directories
Write-Host "Copiando carpetas..."
Copy-Item -Path "$sourceDir\gestion_ordenes" -Destination $tempDir -Recurse
Copy-Item -Path "$sourceDir\ordenes" -Destination $tempDir -Recurse
Copy-Item -Path "$sourceDir\static" -Destination $tempDir -Recurse

# Remove __pycache__ from temp
Get-ChildItem -Path $tempDir -Recurse -Filter "__pycache__" | Remove-Item -Recurse -Force

# Create Zip
Write-Host "Creando ZIP..."
Compress-Archive -Path "$tempDir\*" -DestinationPath $zipFile

# Cleanup
Remove-Item -Recurse -Force $tempDir

Write-Host "¡Listo! Archivo creado en: $zipFile"
