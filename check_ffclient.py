import pyodbc

conn_str = r"DRIVER={ODBC Driver 17 for SQL Server};SERVER=(localdb)\MSSQLLocalDB;DATABASE=MELFA_PRUEBA;Trusted_Connection=yes;"
conn = pyodbc.connect(conn_str)
c = conn.cursor()

try:
    c.execute("SELECT TOP 1 * FROM ffclient WHERE cgo_cli=641")
    cols = [col[0] for col in c.description]
    row = c.fetchone()
    print("Columnas ffclient:", cols)
    print("Muestra:", row)
except Exception as e:
    print(str(e))
