
import zipfile
import os
from pathlib import Path

def create_update_zip():
    base_dir = Path.cwd()
    output_filename = 'update_web.zip'
    
    files_to_include = [
        'core/settings.py',
    ]
    
    dirs_to_include = ['web', 'static']

    with zipfile.ZipFile(output_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add individual files
        for file_path in files_to_include:
            full_path = base_dir / file_path
            if full_path.exists():
                zipf.write(full_path, arcname=file_path)
                print(f"Added: {file_path}")
        
        # Add directories recursively
        for dir_name in dirs_to_include:
            dir_path = base_dir / dir_name
            if dir_path.exists():
                for root, dirs, files in os.walk(dir_path):
                    for file in files:
                        # Skip pycache
                        if '__pycache__' in root:
                            continue
                        file_path = Path(root) / file
                        arcname = file_path.relative_to(base_dir)
                        zipf.write(file_path, arcname=arcname)
                        print(f"Added: {arcname}")
                
    print(f"Created {output_filename}")

if __name__ == "__main__":
    create_update_zip()
