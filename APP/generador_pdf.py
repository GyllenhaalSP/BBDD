"""
 By GyllenhaalSP mar 2023 @ https://github.com/GyllenhaalSP.
"""
import os

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


class PDFGenerator:
    def __init__(self, data, filename="tabla.pdf", title="Tabla"):
        self.data = data
        self.filename = filename
        self.title = title

    def generar_pdf(self):
        # Generar el contenido del PDF
        c = canvas.Canvas(self.filename, pagesize=A4)
        text = c.beginText(20, 800)
        text.setFont("Helvetica", 10)
        # text.textLines(self.title)
        text.textLines(self.data)
        c.drawText(text)
        c.showPage()
        c.save()

    def eliminar_pdf(self):
        os.remove(self.filename)
