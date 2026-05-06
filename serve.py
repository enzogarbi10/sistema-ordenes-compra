"""
Script para correr el servidor Django con waitress (compatible con Windows).
Uso: python serve.py
"""
import os
import sys

# Asegurarse de que el directorio del proyecto esté en el path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

from waitress import serve
from core.wsgi import application

if __name__ == '__main__':
    host = '0.0.0.0'
    port = 8000
    threads = 6
    print(f"✅ Servidor Django iniciado en http://{host}:{port}")
    print(f"   Threads: {threads}")
    print("   Presioná Ctrl+C para detener.\n")
    serve(application, host=host, port=port, threads=threads)
