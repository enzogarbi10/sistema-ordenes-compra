import pyodbc

conn_str = r"DRIVER={ODBC Driver 17 for SQL Server};SERVER=(localdb)\MSSQLLocalDB;DATABASE=MELFA_PRUEBA;Trusted_Connection=yes;"
conn = pyodbc.connect(conn_str)
c = conn.cursor()

try:
    c.execute("""
    SELECT o.id, o.id_ele, o.nro_odt, o.cgo_cli, c.nom_cli, o.den_ele, o.den_var, o.cantidad
    FROM wwordele o
    LEFT JOIN ffclient c ON o.cgo_cli = c.cgo_cli
    WHERE o.nro_odt = 38839
    """)
    rows = c.fetchall()
    
    print(f"Buscando OT 38839 en wwordele...")
    print(f"Total items encontrados: {len(rows)}\n")
    
    for row in rows:
        print(f"Item ID: {row.id} - Ele ID: {row.id_ele}")
        print(f"Cliente: [{row.cgo_cli}] {row.nom_cli}")
        print(f"Elemento: {row.den_ele}")
        print(f"Variedad/Detalle: {row.den_var}")
        print(f"Cantidad: {row.cantidad}")
        print("-" * 40)
        
except Exception as e:
    print(str(e))
