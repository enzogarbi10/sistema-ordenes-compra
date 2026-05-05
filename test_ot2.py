import pyodbc
import sys

try:
    conn_str = r"DRIVER={ODBC Driver 17 for SQL Server};SERVER=(localdb)\MSSQLLocalDB;DATABASE=MELFA_PRUEBA;Trusted_Connection=yes;"
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    
    cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'")
    tablas = [t[0] for t in cursor.fetchall()]
    
    for tabla in tablas:
        try:
            cursor.execute(f"SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{tabla}'")
            cols = [c[0] for c in cursor.fetchall()]
            
            # Check if 38839 is in any column
            for col in cols:
                if 'num' in col.lower() or 'id' in col.lower() or 'cod' in col.lower() or 'ot' in col.lower() or 'nro' in col.lower() or 'ord' in col.lower():
                    cursor.execute(f"SELECT TOP 1 * FROM [{tabla}] WHERE [{col}] = '38839' OR [{col}] = 38839")
                    row = cursor.fetchone()
                    if row:
                        print(f"!!! ENCONTRADA 38839 en TABLA: {tabla} | COLUMNA: {col}")
                        # Print row info zip with cols
                        for c, v in zip(cols, row):
                            print(f"  {c}: {v}")
                        print("-" * 40)
                        break # Go to next table
        except Exception as e:
            pass

    cursor.close()
    conn.close()
except pyodbc.Error as e:
    print("Error:", e)
