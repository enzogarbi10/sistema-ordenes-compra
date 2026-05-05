import pyodbc
import sys

try:
    print("Conectando a (localdb)\\MSSQLLocalDB, BD: MELFA_PRUEBA...")
    conn_str = r"DRIVER={ODBC Driver 17 for SQL Server};SERVER=(localdb)\MSSQLLocalDB;DATABASE=MELFA_PRUEBA;Trusted_Connection=yes;"
    conn = pyodbc.connect(conn_str)
    
    cursor = conn.cursor()
    
    # List all tables to find the right one
    cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'")
    tablas = cursor.fetchall()
    
    print("Buscando tablas relacionadas con Órdenes de Trabajo...")
    encontradas = False
    for t in tablas:
        tabla = t[0].lower()
        if 'orden' in tabla or 'trabajo' in tabla or 'ot' in tabla or 'compro' in tabla or 'pedido' in tabla or 'produccion' in tabla:
             encontradas = True
             print(f"\n-> Tabla: {t[0]}")
             cursor.execute(f"SELECT COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{t[0]}'")
             cols = [c[0] for c in cursor.fetchall()]
             print("Columnas:", ", ".join(cols[:15]) + ("..." if len(cols) > 15 else ""))
             
             # Buscar la Orden 38839 si alguna columna se parece a "numero", "codigo", "id", "ot"
             for col in cols:
                if 'num' in col.lower() or 'id' in col.lower() or 'cod' in col.lower() or 'ot' in col.lower() or 'nro' in col.lower():
                    try:
                        cursor.execute(f"SELECT TOP 1 * FROM [{t[0]}] WHERE [{col}] = '38839' OR [{col}] = 38839")
                        row = cursor.fetchone()
                        if row:
                            print(f"!!! ENCONTRADA ORDEN 38839 en tabla {t[0]} por columna {col}")
                            print("Valores:", [str(v)[:50] for v in row])
                            break
                    except Exception as ex:
                        pass

    if not encontradas:
        print("\nNo se encontraron tablas con nombres parecidos a 'orden', 'trabajo', 'ot', 'comprobante' etc.")
        print("Muestra de todas las tablas disponibles:")
        print([t[0] for t in tablas])

    cursor.close()
    conn.close()
except pyodbc.Error as e:
    print("Error de pyodbc:", e)
except Exception as e:
    print("Error general:", e)
