from flask import Flask, render_template, request, jsonify, send_file
import os
import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import math
import io
import warnings

warnings.filterwarnings("ignore", category=UserWarning, message=".*SQLAlchemy.*")

base_dir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__,
            static_folder=os.path.join(base_dir, '../web/static'),
            template_folder=os.path.join(base_dir, '../web/templates'))
app.config['DEBUG'] = True


# Preveri obstoj tabele v bazi in vrne število stolpcev in vrstic
def check_table_exists(table_name):
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password="2354piki",
            database="main_data10"
        )
        cursor = conn.cursor()

        # Preveri, ali tabela obstaja
        cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
        result = cursor.fetchone()
        if not result:
            cursor.close()
            conn.close()
            return {"exists": False, "columns": 0, "rows": 0}

        # Preštej stolpce
        cursor.execute(f"DESCRIBE {table_name}")
        columns = cursor.fetchall()
        column_count = len(columns)

        # Preštej vrstice
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        row_count = cursor.fetchone()[0]

        cursor.close()
        conn.close()
        return {"exists": True, "columns": column_count, "rows": row_count}

    except Exception as e:
        print(f"Napaka: {e}")
        return {"exists": False, "columns": 0, "rows": 0}


# API za preverjanje tabele
@app.route('/check_table', methods=['GET'])
def check_table():
    start_unix = request.args.get('start')
    end_unix = request.args.get('end')
    table_name = f"main_tab_{start_unix}_{end_unix}"
    details = check_table_exists(table_name)
    return jsonify(details)


# API za pridobivanje statusa ur
@app.route('/get_hour_status', methods=['GET'])
def get_hour_status():
    year = request.args.get('year')
    month = request.args.get('month')
    day = request.args.get('day')

    # Pretvori mesec iz števila v ime
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'Maj', 'Jun', 'Jul', 'Avg', 'Sep', 'Okt', 'Nov', 'Dec']
    try:
        month = months[int(month) - 1]
    except (ValueError, IndexError):
        return jsonify({"error": "Invalid month"}), 400

    # Oblikuj predpono za iskanje
    prefix = f"{year}_{month}_{day}_"

    # Preberi ure.txt
    status = ["w"] * 24
    try:
        with open('/var/www/project/database/ure.txt', 'r') as file:
            for line in file:
                parts = line.strip().split(' ')
                if len(parts) == 2:
                    time_prefix, count = parts
                    if time_prefix.startswith(prefix):
                        hour = int(time_prefix.split('_')[-1])
                        count = int(count)
                        if count == 3600:
                            status[hour] = "g"
                        else:
                            status[hour] = "r"
    except FileNotFoundError:
        return jsonify({"error": "ure.txt not found"}), 500
    
    return jsonify(status)


# API za pridobivanje statusa minut
@app.route('/get_minute_status', methods=['GET'])
def get_minute_status():
    year = request.args.get('year')
    month = request.args.get('month')
    day = request.args.get('day')
    hour = request.args.get('hour')

    # Pretvori mesec iz števila v ime
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'Maj', 'Jun', 'Jul', 'Avg', 'Sep', 'Okt', 'Nov', 'Dec']
    try:
        month = months[int(month) - 1]
    except (ValueError, IndexError):
        return jsonify({"error": "Invalid month"}), 400

    # Oblikuj predpono za iskanje
    prefix = f"{year}_{month}_{day}_{hour}_"

    # Preberi minute.txt
    status = ["w"] * 6
    try:
        with open('/var/www/project/database/minute.txt', 'r') as file:
            for line in file:
                parts = line.strip().split(' ')
                if len(parts) == 2:
                    time_prefix, count = parts
                    if time_prefix.startswith(prefix):
                        index = int(time_prefix.split('_')[-1]) // 10
                        count = int(count)
                        if count == 600:
                            status[index] = "g"
                        else:
                            status[index] = "r"
    except FileNotFoundError:
        return jsonify({"error": "minute.txt not found"}), 500

    return jsonify(status)


# API za izris grafa
@app.route('/graph_lat_lon', methods=['GET'])
def plot_lat_lon():
    # Prebere ime tabele iz parametrov
    table_name = request.args.get('table', default='', type=str)
    first_time_unix = int(table_name.split('_')[2])

    # Povezava z MySQL bazo
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="2354piki",
        database="main_data10"
    )
    query = f"SELECT time_unix, lat, lon FROM {table_name}"
    df = pd.read_sql(query, conn)
    conn.close()

    # Pretvori tipe podatkov in preveri manjkajoče vrednosti
    df['time_unix'] = pd.to_numeric(df['time_unix'], errors='coerce')
    df['lat'] = pd.to_numeric(df['lat'], errors='coerce')  # Pretvori v float
    df['lon'] = pd.to_numeric(df['lon'], errors='coerce')  # Enako za lon

    # Preveri, ali so podatki prazni
    if df['lat'].dropna().empty or df['lon'].dropna().empty:
        return jsonify({"error": "Podatki za lat ali lon niso na voljo."}), 400  # Vrni napako HTTP 400

    # Izračunaj čas od začetka
    df['time_since_start'] = df['time_unix'] - first_time_unix

    # Preračunaj razdalje v cm
    meters_per_degree_lat = 111132.92
    meters_per_degree_lon = meters_per_degree_lat * math.cos(math.radians(df['lat'].dropna().iloc[0]))  # Preverjena vrednost

    df['lat_cm'] = (df['lat'] - df['lat'].iloc[0]) * meters_per_degree_lat * 10
    df['lon_cm'] = (df['lon'] - df['lon'].iloc[0]) * meters_per_degree_lon * 10

    # Izriši graf
    plt.figure(figsize=(10, 6))
    plt.plot(df['time_since_start'], df['lat_cm'], label='Latitudna Deviacija [cm]', color='red', marker='o', markersize=0.01)
    plt.plot(df['time_since_start'], df['lon_cm'], label='Longitudna Deviacija [cm]', color='blue', marker='o', markersize=0.01)

    # Prilagodi meje Y osi (±10 %)
    min_val = min(df[['lat_cm', 'lon_cm']].min())
    max_val = max(df[['lat_cm', 'lon_cm']].max())
    razlika = max_val - min_val
    plt.ylim(min_val - 0.05 * razlika, max_val + 0.05 * razlika)
    plt.subplots_adjust(left=0.1, right=0.97, top=0.96, bottom=0.08)

    time_seconds = df['time_since_start']
    delta_t = time_seconds.iloc[-1] - time_seconds.iloc[0]
    plt.xlim(0, delta_t)

    # Nastavitve grafov
    plt.xlabel('Čas [s]')
    plt.ylabel('Deviacija [cm]')
    plt.title('Latitudna in Longitudialna deviacija od začetne vrednosti')
    plt.legend()
    plt.grid(True)


    # Shrani graf kot PNG
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plt.close()
    return send_file(img, mimetype='image/png')


@app.route('/graph_sv', methods=['GET'])
def graph_sv():
    # Preberi ime tabele iz parametrov
    table_name = request.args.get('table', default='', type=str)
    first_time_unix = int(table_name.split('_')[2])

    # Povezava z MySQL bazo
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="2354piki",
        database="main_data10"
    )
    query = f"SELECT * FROM {table_name}"
    df = pd.read_sql(query, conn)
    conn.close()

    # Pretvori tipe podatkov in pripravi time_since_start
    df['time_unix'] = pd.to_numeric(df['time_unix'], errors='coerce')
    df['time_since_start'] = df['time_unix'] - first_time_unix

    # Najde vse stolpce, ki ustrezajo vzorcu 'sv_*_cno'
    sv_columns = [col for col in df.columns if col.startswith('sv_') and col.endswith('_cno')]

    # Preveri, ali stolpcev sploh ni
    if not sv_columns:
        return jsonify({"status": "empty"})  # Vrnemo 'empty', če ni ustreznih stolpcev

    # Pretvori vrednosti v float in zamenjaj 0 z NaN
    # Zamenjaj neveljavne vrednosti (vključno z '<NA>' in 'NULL') z np.nan
    df[sv_columns] = df[sv_columns].replace(['<NA>', 'NULL', ''], np.nan)

    # Pretvori stolpce varno v float z ohranitvijo dolžine
    for col in sv_columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')  # Pretvori neveljavne v np.nan

    # Zamenjaj vrednosti 0 z np.nan
    df[sv_columns] = df[sv_columns].replace(0, np.nan)

    df[sv_columns] = df[sv_columns].replace(0, np.nan)


    # Preveri, ali so vsi podatki NaN (manjkajoči) v vseh stolpcih
    if df[sv_columns].isna().all().all():  # Preveri vse vrednosti
        return jsonify({"status": "empty"})  # Vrne 'empty', če so vsi podatki NaN

    # Priprava grafov
    time_seconds = df['time_since_start']
    delta_t = time_seconds.iloc[-1] - time_seconds.iloc[0]

    plt.figure(figsize=(10, 6))
    plt.title('C/N0 vrednosti GNSS satelitov')
    plt.xlabel('Čas [s]')
    plt.ylabel('C/N0 [dB]')

    # Barvna paleta za ločevanje linij
    colors = plt.cm.tab20(np.linspace(0, 1, len(sv_columns)))

    for idx, col in enumerate(sv_columns):
        plt.plot(time_seconds, df[col], label=col, color=colors[idx], marker='o', markersize=1, linewidth=1)


    plt.grid(True)
    plt.xlim(0, delta_t)
    plt.ylim(0, 35)
    #plt.tight_layout()
    plt.subplots_adjust(left=0.1, right=0.97, top=0.96, bottom=0.08)
    # Shrani graf kot PNG
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plt.close()
    return send_file(img, mimetype='image/png')


@app.route('/ml_detector_data', methods=['GET'])
def ml_detector_data():
    file_path = '/var/www/project/database/ml_ranked_jan.txt'
    lines = []
    try:
        with open(file_path, 'r') as f:
            lines = f.read().strip().split('\n')
    except FileNotFoundError:
        return jsonify([])

    data_list = []
    for line in lines:
        # Vsaka vrstica: "main_tab_1736034600_1736035199 45"
        parts = line.strip().split()
        if len(parts) < 2:
            continue
        table_name = parts[0]
        try:
            score = int(parts[1])
        except ValueError:
            score = 0

        # Imamo npr. first_unix = 1736034600 iz "main_tab_1736034600_1736035199"
        tn_parts = table_name.split('_')
        if len(tn_parts) >= 3:
            try:
                first_unix = int(tn_parts[2])
            except ValueError:
                first_unix = 0
        else:
            first_unix = 0

        data_list.append({
            "table_name": table_name,
            "score": score,
            "first_unix": first_unix
        })

    # Sortiranje po score padajoče
    data_list.sort(key=lambda x: x["score"], reverse=True)

    return jsonify(data_list)



@app.route('/')
def home():
    return render_template('pick_time.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
