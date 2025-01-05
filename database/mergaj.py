import mysql.connector
import pandas as pd
import json

# Povezava na MySQL database za branje iz test2
conn_test2 = mysql.connector.connect(
    host="localhost",
    user="root",
    password="2354piki",
    database="test2"
)

cursor_test2 = conn_test2.cursor()

# Povezava na MySQL database za pisanje v main_data
conn_main = mysql.connector.connect(
    host="localhost",
    user="root",
    password="2354piki",
    database="main_data"
)

cursor_main = conn_main.cursor()

# vrne seznam tabel iz test2 baze urejenih po času ustvarjanja
cursor_test2.execute("""
    SELECT table_name
    FROM information_schema.tables
    WHERE table_schema = 'test2'
    ORDER BY create_time;
""")
tables = [table[0] for table in cursor_test2.fetchall()]

# Nastavitve za kombiniranje tabel
group_size = 60  # Število tabel v eni skupini

while len(tables) >= group_size:
    # Ustvari set unikatnih stolpcev
    unique_columns = set()

    # Preberi vse tabele in zberi stolpce
    for table in tables[:group_size]:
        cursor_test2.execute(f"DESCRIBE {table}")
        columns = [column[0] for column in cursor_test2.fetchall()]
        unique_columns.update(columns)

    # Pretvori v seznam za vrstni red
    unique_columns = list(unique_columns)

    # Ustvari novo tabelo
    first_table = tables[0]
    last_table = tables[group_size - 1]

    cursor_test2.execute(f"SELECT MIN(time_unix) FROM {first_table}")
    start_unix = int(cursor_test2.fetchone()[0])

    cursor_test2.execute(f"SELECT MAX(time_unix) FROM {last_table}")
    end_unix = int(cursor_test2.fetchone()[0])

    new_table_name = f"main_tab_{start_unix}_{end_unix}"

    # SQL za ustvarjanje velike tabele
    create_sql = f"CREATE TABLE {new_table_name} (id INT AUTO_INCREMENT PRIMARY KEY, "
    create_sql += ", ".join([f"{col} VARCHAR(255)" for col in unique_columns]) + ")"
    cursor_main.execute(create_sql)

    # Združevanje podatkov
    for table in tables[:group_size]:
        cursor_test2.execute(f"SELECT * FROM {table}")
        rows = cursor_test2.fetchall()
        col_names = [desc[0] for desc in cursor_test2.description]

        for row in rows:
            data = dict(zip(col_names, row))
            values = [data.get(col, 'NULL') for col in unique_columns]
            insert_sql = f"INSERT INTO {new_table_name} ({', '.join(unique_columns)}) VALUES ({', '.join(['%s'] * len(values))})"
            cursor_main.execute(insert_sql, values)

        # Izbriši tabelo iz test2 po uporabi
        cursor_test2.execute(f"DROP TABLE {table}")

    # Posodobi preostale tabele in indeks
    tables = tables[group_size:]

# Commit in zaključek
conn_main.commit()
cursor_test2.close()
conn_test2.close()
cursor_main.close()
conn_main.close()
