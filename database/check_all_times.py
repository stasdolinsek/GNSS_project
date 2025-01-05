import mysql.connector

# Funkcija za pretvorbo UNIX časa v datum
def unix_to_datetime(unix_time):
    from datetime import datetime
    dt = datetime.utcfromtimestamp(unix_time)
    return f"{dt.year}_{dt.strftime('%b')}_{dt.day}_{dt.hour}_{dt.minute}"

# Povezava z bazo
connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="2354piki",
    database="main_data10"
)
cursor = connection.cursor()

# Poišči vse tabele v bazi
cursor.execute("SHOW TABLES")
tables = cursor.fetchall()

output = []
row_counts = {}

# Preberi začetni in končni UNIX čas iz imena tabele
for table in tables:
    table_name = table[0]
    try:
        _, start_unix, end_unix = table_name.split('_')[-3:]
        start_time = unix_to_datetime(int(start_unix))
        # Preštej vrstice v tabeli
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        output.append(f"{start_time} {count}")

        # Beleži število vrstic po uri
        prefix = '_'.join(start_time.split('_')[:4])
        if prefix in row_counts:
            row_counts[prefix] += count
        else:
            row_counts[prefix] = count

    except ValueError:
        continue

# Shrani rezultat v datoteko minute.txt
with open("/var/www/project/database/minute.txt", "w") as file:
    for line in output:
        file.write(line + "\n")

print("Podatki so shranjeni v minute.txt.")

# Shrani v ure.txt, če je število zapisov 6
with open("/var/www/project/database/ure.txt", "w") as file:
    for prefix, count in row_counts.items():
        if count >= 6:  # Minimalno število vrstic
            file.write(f"{prefix} {count}\n")

print("Podatki so shranjeni v ure.txt.")

# Zapri povezavo
cursor.close()
connection.close()
