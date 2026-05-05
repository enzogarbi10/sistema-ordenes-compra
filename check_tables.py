import pyodbc

conn_str = r"DRIVER={ODBC Driver 17 for SQL Server};SERVER=(localdb)\MSSQLLocalDB;DATABASE=MELFA_PRUEBA;Trusted_Connection=yes;"
conn = pyodbc.connect(conn_str)
c = conn.cursor()

c.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME LIKE '%cli%'")
print([t[0] for t in c.fetchall()])

try:
    c.execute("SELECT * FROM coclient WHERE cgo_cli=641")
    cols = [col[0] for col in c.description]
    row = c.fetchone()
    if row:
        print(list(zip(cols, row)))
except Exception as e:
    print(str(e))
