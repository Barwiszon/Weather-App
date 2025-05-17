import os
from fpdf import FPDF

def generate_pdf_report(weather_data, df=None, filename="weather_report.pdf"):
    pdf = FPDF()
    pdf.add_page()

    current_dir = os.path.dirname(os.path.abspath(__file__))
    font_dir = os.path.join(current_dir, "fonts")

    font_path_regular = os.path.join(font_dir, "DejaVuSansCondensed.ttf")
    font_path_bold = os.path.join(font_dir, "DejaVuSansCondensed-Bold.ttf")

    if not os.path.exists(font_path_regular) or not os.path.exists(font_path_bold):
        raise FileNotFoundError("Nie znaleziono plików czcionek w katalogu 'fonts'. Pobierz je i umieść w tym folderze.")

    pdf.add_font("DejaVu", "", font_path_regular, uni=True)
    pdf.add_font("DejaVu", "B", font_path_bold, uni=True)

    pdf.set_font("DejaVu", style="B", size=14)
    pdf.cell(0, 10, "Raport pogodowy", ln=True, align="C")
    pdf.ln(10)

    pdf.set_font("DejaVu", size=10)
    pdf.cell(0, 10, "Polskie znaki: ą, ć, ę, ł, ń, ó, ś, ź, ż", ln=True)
    pdf.ln(5)

    if weather_data:
        pdf.set_font("DejaVu", style="B", size=11)
        pdf.cell(0, 10, "Dane pogodowe:", ln=True)
        pdf.set_font("DejaVu", size=10)

        for key, value in weather_data.items():
            pdf.multi_cell(0, 8, f"{key}: {value}")
        pdf.ln(5)

    if df is not None:
        pdf.set_font("DejaVu", style="B", size=11)
        pdf.cell(0, 10, "Statystyki:", ln=True)
        pdf.set_font("DejaVu", size=10)

        summary = df.describe()
        for index, row in summary.iterrows():
            pdf.multi_cell(0, 8, f"{index}: {row.to_dict()}")
        pdf.ln(5)

    pdf.output(filename)
    print(f"Raport PDF zapisany jako {filename}")

