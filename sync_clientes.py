import pyodbc
import requests
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde un archivo .env si existe
load_dotenv()

# ==========================================
# CONFIGURACIÓN DE TU BASE DE DATOS LOCAL
# ==========================================
# IMPORTANT: Asegurate de usar el SERVER, DATABASE y credenciales de tu servidor de producción Real
SQL_SERVER = os.getenv('SQL_SERVER', r'(localdb)\MSSQLLocalDB') # Cambiar por tu servidor real (Ej: SRV-SQL01)
SQL_DATABASE = os.getenv('SQL_DATABASE', 'MELFA')                # Asumiendo que es MELFA

# Como estamos usando Seguridad Integrada de Windows por defecto, no enviamos USER/PASS
# Si tu server de producción requiere usuario de SQL Server (SA u otro), agregalos aquí y cambiá el connection_string.

# Consulta para obtener los clientes con todos sus datos
# Basado en la tabla ffclient que encontramos.
SQL_QUERY = """
SELECT 
    cgo_cli,
    nom_cli, 
    dom_cli, 
    loc_cli, 
    nro_cli, 
    nro_tel, 
    contact, 
    estado 
FROM ffclient
"""

# ==========================================
# CONFIGURACIÓN DE TU WEB APP
# ==========================================
# Cambiá esto por la URL de tu sitio web en PythonAnywhere luego
WEB_API_URL = os.getenv('WEB_API_URL', 'https://agmelfa.pythonanywhere.com/sistema/api/sincronizar_clientes/')

# Esta clave tiene que ser la misma que esté configurada en el settings.py de tu web (SYNC_SECRET_KEY)
SYNC_SECRET_KEY = os.getenv('SYNC_SECRET_KEY', 'default-insecure-sync-key-123')


def obtener_clientes_sql():
    """Conecta a SQL Server y obtiene una lista de diccionarios con clientes."""
    try:
        # ATENCIÓN: Si usas LocalDB usa np:\\.\pipe\LOCALDB#421A15E6\tsql\query
        # Si usas tu SQL Server normal de red, usá SQL_SERVER
        # conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={SQL_SERVER};DATABASE={SQL_DATABASE};Trusted_Connection=yes;'
        
        # PARA ESTA PRUEBA ESTAMOS APUNTANDO A LA BASE RESTAURADA "MELFA_PRUEBA" via pipe LocalDB:
        conn_str = (
            r"DRIVER={ODBC Driver 17 for SQL Server};"
            r"SERVER=(localdb)\MSSQLLocalDB;"
            r"AttachDbFilename=E:\BasesSQL\TEMP\MELFA_PRUEBA.mdf;"
            r"Database=MELFA_PRUEBA;"
            r"Trusted_Connection=yes;"
            r"TrustServerCertificate=yes;"
        )
        
        print(f"Conectando a SQL Server: {SQL_SERVER}...")
        
        # Conectar a la base de datos
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        print("Ejecutando consulta...")
        cursor.execute(SQL_QUERY)
        
        clientes = []
        for row in cursor:
            # Limpiamos todos los valores para que no tengan espacios en blanco de mas o sean None
            # row = [cgo_cli, nom_cli, dom_cli, loc_cli, nro_cli, nro_tel, contact, estado]
            nombre = str(row.nom_cli).strip() if row.nom_cli else ''
            
            if not nombre:
                continue # Evitar clientes vacios
                
            cliente_dict = {
                "codigo": str(row.cgo_cli).strip() if row.cgo_cli else '',
                "nombre": nombre,
                "direccion": str(row.dom_cli).strip() if row.dom_cli else '',
                "localidad": str(row.loc_cli).strip() if row.loc_cli else '',
                "cuit": str(row.nro_cli).strip() if row.nro_cli else '',
                "telefono": str(row.nro_tel).strip() if row.nro_tel else '',
                "contacto": str(row.contact).strip() if row.contact else '',
                "estado": str(row.estado).strip() if row.estado else ''
            }
            clientes.append(cliente_dict)
                
        # Cerrar conexión
        cursor.close()
        conn.close()
        
        print(f"Se encontraron {len(clientes)} clientes en la base de datos local.")
        return clientes
        
    except Exception as e:
        print(f"ERROR conectando a SQL Server: {e}")
        return None

def enviar_a_web(clientes):
    """Envía la lista de clientes a la API de Django."""
    try:
        if not clientes:
            print("No hay clientes para enviar.")
            return

        print(f"Enviando datos a {WEB_API_URL}...")
        
        headers = {
            'Content-Type': 'application/json',
            'HTTP_X_SYNC_SECRET': SYNC_SECRET_KEY,
            'X-SYNC-SECRET': SYNC_SECRET_KEY, # enviamos en ambos formatos por si acaso
        }
        
        payload = {
            'clientes': clientes
        }
        
        response = requests.post(WEB_API_URL, json=payload, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print("OK - ¡Sincronización exitosa!")
            print(f"- Clientes transferidos recibidos en la web: {data.get('total_recibidos')}")
            print(f"- Clientes NUEVOS creados: {data.get('nuevos_creados')}")
            print(f"- Clientes ACTUALIZADOS: {data.get('ya_existentes')}")
        else:
            print(f"Error del servidor web (Código {response.status_code}): {response.text}")
            
    except Exception as e:
        print(f"ERROR conectando con la web: {e}")


if __name__ == "__main__":
    print("--- INICIANDO EXTRACCIÓN Y SINCRONIZACIÓN DE CLIENTES ---")
    lista_clientes = obtener_clientes_sql()
    
    if lista_clientes is not None:
        enviar_a_web(lista_clientes)
        
    print("--- FIN DE EXTRACCIÓN ---")
