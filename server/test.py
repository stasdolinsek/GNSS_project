from flask import Flask, request, jsonify
import time  # Za umetno zakasnitev
import mysql.connector
from datetime import datetime, timedelta

app = Flask(__name__)

# Povezava z MySQL bazo
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="2354piki",  # Zamenjaj s svojim geslom
    database="test2"
)
cursor = db.cursor()

# Funkcija za brisanje vseh tabel
def drop_all_tables():
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
    cursor.execute("SHOW TABLES;")
    tables = cursor.fetchall()
    print(f"Najdene tabele: {tables}")

    for table in tables:
        try:
            cursor.execute(f"DROP TABLE `{table[0]}`;")
            print(f"Izbrisana tabela: {table[0]}")
        except mysql.connector.Error as err:
            print(f"Napaka pri brisanju tabele {table[0]}: {err}")

    cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
    db.commit()
    print("Vse tabele so bile izbrisane!")

# Pokliči funkcijo na začetku
drop_all_tables()
table_num = 1

# Funkcija za ustvarjanje nove tabele
def create_table(table_name, columns):
    col_defs = "`time_unix` BIGINT, " + ", ".join([f"`{col}` VARCHAR(255)" for col in columns])  # Dodan 'time_unix'
    create_query = f"CREATE TABLE IF NOT EXISTS {table_name} ({col_defs});"
    cursor.execute(create_query)

@app.route('/api/test', methods=['POST'])
def test_api():
    global table_num
    # Zakasnitev 50 ms
    time.sleep(0.05)

    # Prejmi JSON podatke
    data = request.get_json()
    print(f"Prejeto: {data}")

    # Pridobi prvi in zadnji iTOW ter izračunaj unix čas z upoštevanjem +1h
    def calculate_unix_time(entry):
        year = entry['year']
        month = entry['month']
        day = entry['day']
        hour = entry['hour']
        minute = entry['min']
        sec = entry['sec']

        # Upoštevaj časovni zamik za Slovenijo (+1h)
        dt = datetime(year, month, day, hour, minute, sec) + timedelta(hours=1)
        return int(dt.timestamp()), dt

    first_unix, first_dt = calculate_unix_time(data[0])
    last_unix, last_dt = calculate_unix_time(data[-1])

    # Ustvari ime tabele v zahtevanem formatu
    table_prefix = "tab"
    table_name = f"{table_prefix}{table_num}_{first_unix}_{last_unix}"
    print(table_name)
    print(f"Prva meritev: {first_dt.strftime('%d.%m.%Y %H:%M:%S')}, Zadnja meritev: {last_dt.strftime('%d.%m.%Y %H:%M:%S')}")
    table_num += 1

    # Ustvari tabelo z dinamičnimi stolpci
    columns = data[0].keys()
    create_table(table_name, columns)

    # Vstavi podatke v tabelo
    insert_query = f"INSERT INTO {table_name} (time_unix, {', '.join(columns)}) VALUES ({', '.join(['%s'] * (len(columns) + 1))})"
    for row in data:
        unix_time, _ = calculate_unix_time(row)
        values = (unix_time,) + tuple(row.values())
        cursor.execute(insert_query, values)

    db.commit()  # Shrani spremembe v bazo

    return jsonify({"status": "success", "table": table_name})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)  # Poslušaj na vseh IP-jih, port 5000
