"""
 By GyllenhaalSP mar 2023 @ https://github.com/GyllenhaalSP.
"""
import os
from fpdf import FPDF


class PDFGenerator:
    def __init__(self, data, filename="tabla.pdf", title="Tabla", mail=None):
        self.data = data
        self.filename = filename
        self.title = title
        self.mail = mail

    def generar_pdf(self):
        # Crear objeto FPDF
        pdf = FPDF()
        pdf.add_page()

        # Agregar título
        pdf.set_font("Courier", size=16)
        pdf.cell(200, 10, txt=self.title, ln=1, align="C")
        pdf.set_font("Courier", size=16, style="B")
        pdf.cell(200, 10, txt=self.mail, ln=1, align="C")

        # Agregar datos
        pdf.set_font("Courier", size=9)
        for row in self.data.split("\n"):
            print(row)
            pdf.multi_cell(0, 3, txt=row, align="L")

        # Guardar el PDF
        pdf.output(self.filename)

    def eliminar_pdf(self):
        os.remove(self.filename)
