import mysql.connector

# Povezava na MySQL strežnik
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="2354piki"
)
cursor = conn.cursor()

# Pridobi ime baze od uporabnika
db_name = input("Vnesite ime baze, v kateri želite pobrisati vse tabele: ")

# Preveri, če baza obstaja
cursor.execute(f"SHOW DATABASES LIKE '{db_name}'")
db_exists = cursor.fetchone()

if not db_exists:
    print(f"Baza '{db_name}' ne obstaja.")
else:
    # Preklopi na izbrano bazo
    cursor.execute(f"USE {db_name}")

    # Pridobi seznam vseh tabel
    cursor.execute("SHOW TABLES")
    tables = [table[0] for table in cursor.fetchall()]

    if not tables:
        print(f"Baza '{db_name}' ne vsebuje tabel.")
    else:
        # Potrditev brisanja
        confirm = input(f"Ali res želite pobrisati {len(tables)} tabel v bazi '{db_name}'? (da/ne): ").lower()

        if confirm == 'da':
            for table in tables:
                cursor.execute(f"DROP TABLE {table}")
                print(f"Tabela '{table}' je bila pobrisana.")
            print("Vse tabele so bile uspešno pobrisane.")
        else:
            print("Operacija preklicana.")

# Zaključek
cursor.close()
conn.close()
