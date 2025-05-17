import os
from fetch_data import fetch_weather_data, save_weather_data
from analyze_data import analyze_weather_csv
from report import generate_pdf_report

def main():
    city = "Warsaw"
    weather_data = fetch_weather_data(city)
    if weather_data:
        save_weather_data(weather_data)
        csv_file = "weather_history.csv"
        df = analyze_weather_csv(csv_file) if os.path.exists(csv_file) else None
        generate_pdf_report(weather_data, df)

if __name__ == "__main__":
    main()
