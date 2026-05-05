import pyodbc

conn_str = r"DRIVER={ODBC Driver 17 for SQL Server};SERVER=(localdb)\MSSQLLocalDB;DATABASE=MELFA_PRUEBA;Trusted_Connection=yes;"
conn = pyodbc.connect(conn_str)
c = conn.cursor()

c.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE COLUMN_NAME = 'nro_odt'")
tables = [t[0] for t in c.fetchall()]

print("Buscando en tablas con columna 'nro_odt' el valor 38839...")
for t in tables:
    try:
        c.execute(f"SELECT * FROM {t} WHERE nro_odt = 38839")
        row = c.fetchone()
        if row:
            print(f"-> ENCONTRADO 38839 en tabla {t}")
            cols = [col[0] for col in c.description]
            for col_name, val in zip(cols, row):
                print(f"  {col_name}: {val}")
    except Exception as e:
        print(f"Error en {t}: {e}")

# What if it's not nro_odt but some other like 'numero' in 'odt...' tables?
c.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME LIKE '%odt%' OR TABLE_NAME LIKE '%orden%'")
tables_odt = [t[0] for t in c.fetchall()]
print("\nTablas que suenan a ODT o ORDEN:", tables_odt)

for t in tables_odt:
    try:
        c.execute(f"SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME='{t}'")
        cols = [col[0] for col in c.fetchall()]
        for col in cols:
            if 'num' in col.lower() or 'nro' in col.lower() or 'id' in col.lower() or 'ot' in col.lower():
                c.execute(f"SELECT * FROM {t} WHERE {col} = 38839 OR {col} = '38839'")
                row = c.fetchone()
                if row:
                     print(f"-> ENCONTRADO 38839 en {t} por {col}")
                     break
    except Exception:
        pass
