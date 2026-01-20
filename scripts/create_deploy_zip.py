import zipfile
import os
from pathlib import Path

def create_deploy_zip():
    # Define paths
    base_dir = Path.cwd()
    output_filename = 'deploy_sistema.zip'
    
    # Files/Dirs to EXCLUDE
    excludes = {
        'venv', 
        '__pycache__', 
        '.git', 
        '.idea', 
        '.vscode', 
        'emails', 
        'deploy_sistema.zip',
        'SistemaOrdenesCompra.zip',
        'bajada_completa.zip'
    }

    print(f"Creando {output_filename}...")
    
    with zipfile.ZipFile(output_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(base_dir):
            # Modify dirs in-place to skip excluded directories
            dirs[:] = [d for d in dirs if d not in excludes]
            
            for file in files:
                if file in excludes or file.endswith('.pyc') or file.endswith('.log'):
                    continue
                
                file_path = Path(root) / file
                arcname = file_path.relative_to(base_dir)
                
                print(f"Adding: {arcname}")
                zipf.write(file_path, arcname)

    print(f"\nExito! Archivo creado: {output_filename}")

if __name__ == "__main__":
    create_deploy_zip()
