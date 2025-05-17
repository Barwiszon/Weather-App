import pandas as pd

def analyze_weather_csv(file_path):
    df = pd.read_csv(file_path)
    print("Podsumowanie danych:")
    print(df.describe())
    return df
