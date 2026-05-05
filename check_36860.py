import pyodbc

try:
    conn_str = r"DRIVER={ODBC Driver 17 for SQL Server};SERVER=(localdb)\MSSQLLocalDB;DATABASE=MELFA_PRUEBA;Trusted_Connection=yes;"
    conn = pyodbc.connect(conn_str)
    c = conn.cursor()
    
    # Intentamos buscar la OT 36860 en varias tablas (comienza por wwordele)
    print("Buscando 36860 en wwordele...")
    c.execute("""
        SELECT o.id, o.numero, o.cgo_cli, c.nom_cli, o.den_ele, o.den_var, o.cantidad
        FROM wwordele o
        LEFT JOIN ffclient c ON o.cgo_cli = c.cgo_cli
        WHERE o.nro_odt = 36860
    """)
    rows1 = c.fetchall()
    if rows1:
        print(f"ENCONTRADO en wwordele: {len(rows1)} items")
        for r in rows1:
            print(f" -> {r}")
    else:
        print("NO ENCONTRADO en wwordele. Buscando en otras tablas...")
        
    c.close()
    conn.close()
except Exception as e:
    print(f"Error: {e}")
