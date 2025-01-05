import mysql.connector
import pandas as pd

# Definiraj ime tabele
table_name = "main_tab_1735924200_1735924799"

# Izvleček prvega časa iz imena tabele
first_time_unix = int(table_name.split('_')[2])

# Povezava z MySQL bazo
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="2354piki",
    database="main_data10"
)

# Poizvedba za branje podatkov
query = f"SELECT time_unix, lat, lon FROM {table_name}"

# Ustvari DataFrame
df = pd.read_sql(query, conn)

# Zapri povezavo
conn.close()

# Ustvari novi stolpec time_since_start
df['time_unix'] = df['time_unix'].astype(int)

# Izračunaj time_since_start
df['time_since_start'] = df['time_unix'] - first_time_unix

# Izpiši prvih 5 vrstic
print(df.head())
