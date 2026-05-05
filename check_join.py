import pyodbc

conn_str = r"DRIVER={ODBC Driver 17 for SQL Server};SERVER=(localdb)\MSSQLLocalDB;DATABASE=MELFA_PRUEBA;Trusted_Connection=yes;"
conn = pyodbc.connect(conn_str)
c = conn.cursor()

try:
    c.execute("""
    SELECT TOP 1 o.nro_odt, o.cgo_cli, c.den_cli, o.den_var
    FROM wwordele o
    LEFT JOIN ffclient c ON o.cgo_cli = c.cgo_cli
    WHERE o.nro_odt = 38839
    """)
    row = c.fetchone()
    if row:
        print(f"BINGO! OT: {row.nro_odt}, Cliente: [{row.cgo_cli}] {row.den_cli}, Etiqueta: {row.den_var}")
    else:
        print("No se encontró al hacer JOIN.")
except Exception as e:
    print(str(e))
