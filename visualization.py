import matplotlib.pyplot as plt

def generate_weather_plot(df, column="temperature", filename="static/plot.png"):
    plt.figure(figsize=(10, 5))
    plt.plot(df[column])
    plt.title(f"Wykres: {column}")
    plt.xlabel("Index")
    plt.ylabel(column)
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()
    return filename
