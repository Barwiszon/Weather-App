import os
import requests
import pandas as pd
import matplotlib.pyplot as plt
from werkzeug.utils import secure_filename

from flask import (
    Flask, render_template, request,
    redirect, url_for, flash,
    send_file
)
from fpdf import FPDF
from io import BytesIO


API_KEY = None
FLASK_SECRET_KEY = None
try:
    import config
    API_KEY = config.API_KEY
    FLASK_SECRET_KEY = config.FLASK_SECRET_KEY
except ImportError:
    API_KEY = os.environ.get('OWM_API_KEY')
    FLASK_SECRET_KEY = os.environ.get('FLASK_SECRET_KEY')

if not API_KEY:
    raise RuntimeError("Brak klucza OpenWeatherMap (API_KEY).")
if not FLASK_SECRET_KEY:
    raise RuntimeError("Brak sekretu Flask (FLASK_SECRET_KEY).")


BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
FONTS_DIR  = os.path.join(BASE_DIR, 'fonts')
FONT_REG   = os.path.join(FONTS_DIR, 'DejaVuSansCondensed.ttf')
FONT_BOLD  = os.path.join(FONTS_DIR, 'DejaVuSansCondensed-Bold.ttf')

# ---------------------------------------b
app = Flask(__name__)
app.secret_key = FLASK_SECRET_KEY


UPLOAD_FOLDER = 'uploads'
STATIC_FOLDER = 'static'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(STATIC_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/', methods=['GET', 'POST'])
def index():
    """
    Strona główna: formularz wpisania miasta.
    POST: pobranie danych + przygotowanie wykresów + 5-dniowej prognozy.
    """
    weather_data   = None
    dates, temps   = [], []
    hums, winds    = [], []
    cond_counts    = {}
    daily_forecast = []

    if request.method == 'POST':
        city = request.form.get('city')
        if not city:
            flash('Proszę wpisać nazwę miasta.')
            return redirect(url_for('index'))

        # Endpoints
        url_cur = f'https://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={API_KEY}'
        url_fc  = f'https://api.openweathermap.org/data/2.5/forecast?q={city}&units=metric&appid={API_KEY}'

        try:

            r1 = requests.get(url_cur); r1.raise_for_status(); weather_data = r1.json()

            r2 = requests.get(url_fc); r2.raise_for_status(); forecast = r2.json()

            for itm in forecast['list']:
                dt = pd.to_datetime(itm['dt_txt'])
                dates.append(dt.strftime('%Y-%m-%d %H:%M'))
                temps.append(itm['main']['temp'])
                hums.append(itm['main']['humidity'])
                winds.append(itm['wind']['speed'])
                c = itm['weather'][0]['main']
                cond_counts[c] = cond_counts.get(c, 0) + 1


            df_fc = pd.DataFrame([
                {
                    'dt': pd.to_datetime(i['dt_txt']),
                    'temp': i['main']['temp'],
                    'humidity': i['main']['humidity'],
                    'wind': i['wind']['speed']
                }
                for i in forecast['list']
            ]).set_index('dt')

            daily = df_fc.resample('D').agg({
                'temp': ['min','max'],
                'humidity': 'mean',
                'wind': 'mean'
            }).dropna()


            daily.columns = ['tmin','tmax','hum_mean','wind_mean']
            daily = daily.reset_index().head(5)

            # Do listy dla template
            for _, row in daily.iterrows():
                daily_forecast.append({
                    'date': row['dt'].strftime('%Y-%m-%d'),
                    'tmin': f"{row['tmin']:.1f}",
                    'tmax': f"{row['tmax']:.1f}",
                    'hum':  f"{row['hum_mean']:.0f}%",
                    'wind': f"{row['wind_mean']:.1f} m/s"
                })

        except Exception as e:
            flash(f'Błąd pobierania danych: {e}')
            return redirect(url_for('index'))

    return render_template(
        'index.html',
        weather_data=weather_data,
        dates=dates,
        temp_data=temps,
        hum_data=hums,
        wind_data=winds,
        cond_counts=cond_counts,
        daily_forecast=daily_forecast
    )


@app.route('/generate_pdf', methods=['POST'])
def generate_pdf():

    city = request.form.get('city')
    if not city:
        flash('Brak nazwy miasta do wygenerowania PDF.')
        return redirect(url_for('index'))

    # 1) Pobranie danych current + forecast
    url_cur = f'https://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={API_KEY}'
    url_fc  = f'https://api.openweathermap.org/data/2.5/forecast?q={city}&units=metric&appid={API_KEY}'
    try:
        w = requests.get(url_cur); w.raise_for_status(); weather = w.json()
        f = requests.get(url_fc);  f.raise_for_status(); forecast = f.json()
    except Exception as e:
        flash(f'Błąd podczas pobierania do PDF: {e}')
        return redirect(url_for('index'))

    # 2) Budujemy DataFrame z prognozą i agregujemy po datach
    df = pd.DataFrame([
        {
            'dt':          pd.to_datetime(item['dt_txt']),
            'temp':        item['main']['temp'],
            'humidity':    item['main']['humidity'],
            'wind_speed':  item['wind']['speed']
        }
        for item in forecast['list']
    ])
    df['date'] = df['dt'].dt.date
    daily = (
        df.groupby('date')
          .agg(
             tmin = ('temp',       'min'),
             tmax = ('temp',       'max'),
             hum  = ('humidity',   'mean'),
             wind = ('wind_speed', 'mean'),
          )
          .reset_index()
          .head(5)
    )

    # 3) Generujemy wykres temperatury
    plt.figure(figsize=(8, 3))
    plt.plot(df['dt'], df['temp'], marker='o')
    plt.xticks(rotation=45)
    plt.tight_layout()
    buf = BytesIO()
    plt.savefig(buf, format='PNG')
    plt.close()
    buf.seek(0)
    tmp = os.path.join(STATIC_FOLDER, 'tmp_chart.png')
    with open(tmp, 'wb') as img:
        img.write(buf.getbuffer())

    # 4) Tworzymy PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font('DejaVu','', FONT_REG, uni=True)
    pdf.add_font('DejaVu','B', FONT_BOLD, uni=True)

    # 4a) Nagłówek i bieżąca pogoda
    pdf.set_font('DejaVu','B',16)
    pdf.cell(0, 10, f'Raport pogody: {city}', ln=1, align='C')
    pdf.set_font('DejaVu','',12)
    pdf.ln(5)
    pdf.cell(0, 8, f"Temperatura: {weather['main']['temp']:.1f} °C", ln=1)
    pdf.cell(0, 8, f"Wilgotność:  {weather['main']['humidity']} %", ln=1)
    pdf.cell(0, 8, f"Wiatr:       {weather['wind']['speed']} m/s", ln=1)
    pdf.cell(0, 8, f"Opis:        {weather['weather'][0]['description']}", ln=1)

    # 4b) Tabelka 5-dniowa
    pdf.ln(8)
    pdf.set_font('DejaVu','B',14)
    pdf.cell(0, 8, 'Prognoza na 5 dni', ln=1)
    pdf.ln(2)
    pdf.set_font('DejaVu','B',12)
    col_w = [30, 25, 25, 30, 30]
    headers = ['Data','Min °C','Max °C','Śr. wilg.','Śr. wiatr']
    for i, h in enumerate(headers):
        pdf.cell(col_w[i], 8, h, border=1, align='C')
    pdf.ln()
    pdf.set_font('DejaVu','',11)
    for _, row in daily.iterrows():
        pdf.cell(col_w[0], 8, row['date'].strftime('%Y-%m-%d'), border=1, align='C')
        pdf.cell(col_w[1], 8, f"{row['tmin']:.1f}", border=1, align='C')
        pdf.cell(col_w[2], 8, f"{row['tmax']:.1f}", border=1, align='C')
        pdf.cell(col_w[3], 8, f"{row['hum']:.0f}%", border=1, align='C')
        pdf.cell(col_w[4], 8, f"{row['wind']:.1f} m/s", border=1, align='C')
        pdf.ln()

    # 4c) Wstawiamy wykres pod tabelką
    pdf.ln(6)
    pdf.image(tmp, x=10, w=190)

    # 5) Sprzątanie i wysyłka
    try: os.remove(tmp)
    except: pass
    pdf_bytes = pdf.output(dest='S').encode('latin-1')
    return send_file(
        BytesIO(pdf_bytes),
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'{city}_report.pdf'
    )


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'csv'

@app.route('/upload-csv', methods=['GET', 'POST'])
def upload_csv():
    if request.method == 'POST':
        # 1) Odbiór i zapis pliku
        file = request.files.get('csv_file')
        if not file or not allowed_file(file.filename):
            flash('Proszę załadować poprawny plik CSV.')
            return redirect(url_for('upload_csv'))

        filename = secure_filename(file.filename)
        path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(path)

        # 2) Pobranie wartości filtrów
        start = request.form.get('start_date')
        end   = request.form.get('end_date')

        # 3) Wczytanie CSV (parsujemy 'date' jeśli jest)
        try:
            hdrs = pd.read_csv(path, nrows=0).columns.tolist()
            parse_dates = ['date'] if 'date' in hdrs else []
            df = pd.read_csv(path, parse_dates=parse_dates)
        except Exception as e:
            flash(f'Błąd odczytu CSV: {e}')
            return redirect(url_for('upload_csv'))

        # 4) Filtrowanie po dacie
        if 'date' in df.columns:
            if start:
                df = df[df['date'] >= pd.to_datetime(start)]
            if end:
                df = df[df['date'] <= pd.to_datetime(end)]

        # 5) Przygotowanie podglądu, podsumowania i wykresów
        preview_html = df.head(20).to_html(classes='preview-table', index=False)
        summary_html = df.describe().T.to_html(classes='summary-table')

        metrics = {
            'records': len(df),
            'avg_temp': df['temperature'].mean() if 'temperature' in df.columns else None,
            'max_humidity': df['humidity'].max()    if 'humidity'    in df.columns else None,
            'max_wind': df['wind_speed'].max()      if 'wind_speed'  in df.columns else None
        }
        dates_csv    = df['date'].dt.strftime('%Y-%m-%d').tolist() if 'date' in df.columns else []
        temp_csv     = df['temperature'].tolist() if 'temperature' in df.columns else []
        humidity_csv = df['humidity'].tolist()    if 'humidity'    in df.columns else []

        return render_template(
            'upload_success.html',
            filename=filename,
            preview_html=preview_html,
            summary_html=summary_html,
            metrics=metrics,
            dates=dates_csv,
            temp_data=temp_csv,
            humidity_data=humidity_csv,
            has_date_column='date' in df.columns
        )

    # GET
    return render_template('upload_csv.html')


@app.route('/filter-data', methods=['GET', 'POST'])
def filter_data():
    filename       = request.args.get('filename')
    files          = os.listdir(UPLOAD_FOLDER)
    columns        = []
    filtered_table = None

    if filename:
        path = os.path.join(UPLOAD_FOLDER, filename)
        try:
            df = pd.read_csv(path)
            columns = df.columns.tolist()
        except Exception as e:
            flash(f'Błąd odczytu pliku: {e}')
            return redirect(url_for('upload_csv'))

        if request.method == 'POST':
            col = request.form['column']
            val = request.form['value']
            if col not in df.columns:
                flash(f'Kolumna "{col}" nie istnieje.')
                return redirect(url_for('filter_data', filename=filename))
            filtered = df[df[col].astype(str) == val]
            filtered_table = filtered.to_html(classes='filtered-table', index=False)

    return render_template(
        'filter_data.html',
        files=files,
        selected_file=filename,
        columns=columns,
        filtered_table=filtered_table
    )


if __name__ == '__main__':
    app.run(debug=True)
