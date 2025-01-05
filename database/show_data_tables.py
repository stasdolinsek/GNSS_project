import mysql.connector
from datetime import datetime, timezone

# Vprašaj uporabnika za ime baze
database_name = input("Vnesi ime baze za branje: ")

# Povezava na MySQL bazo
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '2354piki',
    'database': database_name
}

# Poveži se na bazo in pridobi vsa imena tabel
connection = mysql.connector.connect(**DB_CONFIG)
cursor = connection.cursor()
cursor.execute("SHOW TABLES")
tables = [table[0] for table in cursor.fetchall()]

# Pretvori časovne žige iz imen tabel
intervals = []
for table in tables:
    parts = table.split('_')
    start = datetime.fromtimestamp(int(parts[2]), tz=timezone.utc)
    end = datetime.fromtimestamp(int(parts[3]), tz=timezone.utc)

    # Preštej vrstice in stolpce za tabelo
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    rows = cursor.fetchone()[0]
    cursor.execute(f"SHOW COLUMNS FROM {table}")
    columns_data = cursor.fetchall()
    columns = len(columns_data)

    print(f"Tabela: {table} | {start.strftime('%H:%M:%S')} - {end.strftime('%H:%M:%S')} | Vrstice: {rows} | Stolpci: {columns}")

cursor.close()
connection.close()
