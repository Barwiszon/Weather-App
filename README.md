# Weather App

Aplikacja webowa napisana w Pythonie z użyciem Flask, umożliwiająca:

- Sprawdzanie aktualnej pogody dla dowolnego miasta (OpenWeatherMap API).  
- Wyświetlanie 5-dniowej prognozy w formie tabeli i wykresów.  
- Generowanie raportu PDF z aktualną pogodą i wykresem prognozy.  
- Wgrywanie własnych plików CSV z danymi pogodowymi, przeglądanie, podsumowywanie i tworzenie wykresów.

---

## 📋 Funkcjonalności

1. **Strona główna**  
   - Formularz wpisania nazwy miasta.  
   - Wyświetlenie aktualnej pogody: temperatura, wilgotność, wiatr, opis.  
   - Zakładki Chart.js: temperatura, wilgotność, prędkość wiatru, warunki pogodowe.  
   - Generowanie PDF (biblioteka FPDF + matplotlib) z raportem.

2. **Upload CSV**  
   - Wgrywanie pliku `.csv` z kolumną `date` i (opcjonalnie) innymi polami.  
   - Podgląd pierwszych 5 wierszy (DataTables.js).  
   - Podsumowanie kolumn numerycznych (pandas `.describe()`).  
   - Metryki: liczba rekordów, średnia temperatura, maks. wilgotność, maks. wiatr.  
   - Wykresy temperatury i wilgotności z Chart.js.

3. **Filtrowanie danych**  
   - Proste filtrowanie wgranych CSV po dowolnej kolumnie i wartości.

---

## 🛠 Technologie

- **Backend**: Python 3.8+, Flask, Requests, pandas, matplotlib, FPDF  
- **Frontend**: HTML5, CSS3, JavaScript, jQuery, Chart.js, DataTables.js  
- **Styling**: własne `static/styles.css`

---

## 🚀 Instalacja i uruchomienie

1. **Sklonuj repozytorium**  
   ```bash
   git clone https://github.com/Barwiszon/Weather-App.git
   cd Weather-App
   ```
2. **Utwórz i aktywuj wirtualne środowisko**
   ```bash
   python -m venv venv
   ```
   Windows
   ```bash
   venv\Scripts\activate
   ```
   macOS / Linux
   ```bash
   source venv/bin/activate
   ```
3.**Zainstaluj zależności**
   ```bash
   pip install -r requirements.txt
   ```
4.**Konfiguracja**
   ```bash
   API_KEY = 'TWÓJ_KLUCZ_OPENWEATHERMAP'
   FLASK_SECRET_KEY = 'JAKIŚ_TAJNY_KLUCZ'
   ```
5.**Uruchom aplikację**
   ```bash
   python app.py
   ```

Aplikacja dostępna pod adresem: http://127.0.0.1:5000
