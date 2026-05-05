import pyodbc

conn_str = r"DRIVER={ODBC Driver 17 for SQL Server};SERVER=(localdb)\MSSQLLocalDB;DATABASE=MELFA_PRUEBA;Trusted_Connection=yes;"
conn = pyodbc.connect(conn_str)
c = conn.cursor()

c.execute("SELECT id, id_ele, numero, senal, den_var FROM wwordele WHERE nro_odt = 38839")
for row in c.fetchall():
    print(row)
