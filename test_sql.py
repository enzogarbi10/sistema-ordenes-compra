import pyodbc
import os

try:
    print("Conectando para consultar MELFA_PRUEBA...")
    conn_str = r"DRIVER={ODBC Driver 17 for SQL Server};SERVER=np:\\.\pipe\LOCALDB#421A15E6\tsql\query;Trusted_Connection=yes;"
    conn = pyodbc.connect(conn_str)
    conn.autocommit = True
    cursor = conn.cursor()
    
    cursor.execute("SELECT TABLE_NAME FROM MELFA_PRUEBA.INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'")
    tablas = cursor.fetchall()
    
    for t in tablas:
        tabla = t[0]
        if 'client' in tabla.lower() or 'cust' in tabla.lower():
             print(f"\n-> Tabla encontrada: {tabla}")
             print("Sus columnas son:")
             cursor.execute(f"SELECT COLUMN_NAME, DATA_TYPE FROM MELFA_PRUEBA.INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{tabla}'")
             for col_name, col_type in cursor.fetchall():
                  print(f"  - {col_name} ({col_type})")
                  
             print("Muestra de datos (primeros 3 registros):")
             try:
                 cursor.execute(f"SELECT TOP 3 * FROM MELFA_PRUEBA.dbo.[{tabla}]")
                 for row in cursor.fetchall():
                     print([str(val)[:50] for val in row])
             except Exception as e:
                 print(f"Error leyendo muestra: {e}")
        
    cursor.close()
    conn.close()
except Exception as e:
    print(f"Error: {e}")
