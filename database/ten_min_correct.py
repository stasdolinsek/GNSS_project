import mysql.connector
import pandas as pd
from sqlalchemy import create_engine
import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)

DB_CONFIG_MAIN = {
    'host': 'localhost',
    'user': 'root',
    'password': '2354piki',
    'database': 'main_data'
}

DB_CONFIG_MAIN10 = {
    'host': 'localhost',
    'user': 'root',
    'password': '2354piki',
    'database': 'main_data10'
}

# 1. Funkcija za zaznavo in preslikavo podatkovnih tipov
def detect_mysql_type(value, column_name):
    """Določi optimalne podatkovne tipe za MySQL glede na vrednosti."""
    try:
        # Poskus konverzije iz niza v število
        if isinstance(value, str):
            if value.upper() == "NULL" or value == '':
                return "VARCHAR(255)"  # Obdrži kot niz, če je 'NULL' ali prazen
            if value.isdigit():
                value = int(value)
            else:
                value = float(value)
    except (ValueError, TypeError):
        pass

    # Preslikava tipov
    if isinstance(value, int):
        if 'cno' in column_name:  # TINYINT za CNO
            return "TINYINT"
        elif -32768 <= value <= 32767:
            return "SMALLINT"
        return "INT"
    elif isinstance(value, float):
        return "FLOAT"
    else:
        return "VARCHAR(255)"  # Privzeto za nize

# 2. Pridobi in združi tabele
def fetch_and_merge_tables():
    connection = mysql.connector.connect(**DB_CONFIG_MAIN)
    cursor = connection.cursor()
    cursor.execute("SHOW TABLES")
    tables = [table[0] for table in cursor.fetchall()]

    engine = create_engine('mysql+mysqlconnector://root:2354piki@localhost/main_data')

    all_columns = set()
    data_frames = []
    last_tab_columns = set()

    for table in tables:
        query = f"SELECT * FROM {table}"
        df = pd.read_sql(query, con=engine)
        all_columns.update(df.columns)
        data_frames.append(df)
        last_tab_columns = set(df.columns)

    combined_df = pd.DataFrame(columns=list(all_columns))
    for df in data_frames:
        for col in all_columns - set(df.columns):
            df[col] = pd.NA

        # Zaznaj tipe in pretvori stolpce
        if not df.empty:
            for col in df.columns:
                sample_value = df[col].dropna().iloc[0] if not df[col].dropna().empty else None
                mysql_type = detect_mysql_type(sample_value, col)

                if mysql_type in ["INT", "SMALLINT", "TINYINT"]:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
                elif mysql_type == "FLOAT":
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0).astype(float)
                else:
                    df[col] = df[col].astype(str)  # Pretvori v niz, če ni številka

        combined_df = pd.concat([combined_df, df], ignore_index=True)

    combined_df = combined_df.sort_values(by='time_unix')
    cols = ['id', 'time_unix'] + [col for col in combined_df.columns if col not in ['id', 'time_unix']]
    combined_df = combined_df[cols]

    cursor.close()
    connection.close()
    return combined_df, last_tab_columns

# 3. Pridobi 10-minutne intervale
def get_intervals_unix(df):
    df['timestamp'] = pd.to_datetime(df['time_unix'], unit='s')
    start_time = df['timestamp'].min()
    end_time = df['timestamp'].max()
    first_full_interval = start_time.ceil('10T')
    last_full_interval = end_time.floor('10T')

    full_intervals = []
    current = first_full_interval
    while current < last_full_interval:
        full_intervals.append((int(current.timestamp()), int((current + pd.Timedelta(minutes=10)).timestamp() - 1)))
        current += pd.Timedelta(minutes=10)

    incomplete_end = (int(last_full_interval.timestamp()), int(end_time.timestamp()))
    return full_intervals, incomplete_end

# 4. Shrani intervale
def save_intervals(df, full_intervals, incomplete_end, last_tab_columns):
    main_conn = mysql.connector.connect(**DB_CONFIG_MAIN)
    main_cursor = main_conn.cursor()

    # Izbriši vse tabele iz main_data
    main_cursor.execute("SHOW TABLES")
    tables = [table[0] for table in main_cursor.fetchall()]
    for table in tables:
        main_cursor.execute(f"DROP TABLE {table}")

    main_conn.commit()
    main_cursor.close()
    main_conn.close()

    engine_main10 = create_engine('mysql+mysqlconnector://root:2354piki@localhost/main_data10')
    engine_main = create_engine('mysql+mysqlconnector://root:2354piki@localhost/main_data')

    for start, end in full_intervals:
        interval_df = df[(df['time_unix'] >= start) & (df['time_unix'] <= end)].copy()
        interval_df['time_unix'] = interval_df['time_unix'].astype(str)
        table_name = f"main_tab_{start}_{end}"
        interval_df.to_sql(table_name, con=engine_main10, if_exists='replace', index=False)

    start, end = incomplete_end
    incomplete_df = df[(df['time_unix'] >= start) & (df['time_unix'] <= end)].copy()
    incomplete_df = incomplete_df[list(last_tab_columns)]
    incomplete_df['time_unix'] = incomplete_df['time_unix'].astype(str)
    table_name = f"main_tab_{start}_{end}"
    incomplete_df.to_sql(table_name, con=engine_main, if_exists='replace', index=False)

# Glavna funkcija
def main():
    df, last_tab_columns = fetch_and_merge_tables()
    full_intervals, incomplete_end = get_intervals_unix(df)
    save_intervals(df, full_intervals, incomplete_end, last_tab_columns)

if __name__ == "__main__":
    main()
