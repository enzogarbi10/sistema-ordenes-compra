import zipfile
import os
import shutil

# Rutas
ZIP_PATH = r"..\bajada_completa.zip"
PROJECT_ROOT = "."

def extract_content():
    if not os.path.exists(ZIP_PATH):
        print(f"Error: No se encuentra {ZIP_PATH}")
        return

    print("Abriendo ZIP...")
    with zipfile.ZipFile(ZIP_PATH, 'r') as zip_ref:
        # 1. Extraer DB
        if 'db.sqlite3' in zip_ref.namelist():
            print("Extrayendo db.sqlite3...")
            zip_ref.extract('db.sqlite3', PROJECT_ROOT)
        else:
            print("WARNING: db.sqlite3 no encontrado en el ZIP")

        # 2. Extraer Media
        members = [m for m in zip_ref.namelist() if m.startswith('media/')]
        if members:
            print(f"Extrayendo {len(members)} archivos de media/...")
            zip_ref.extractall(PROJECT_ROOT, members=members)
        else:
            print("WARNING: carpeta media/ no encontrada en el ZIP")

    print("Extracción completada.")

if __name__ == "__main__":
    extract_content()
