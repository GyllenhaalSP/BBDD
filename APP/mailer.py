"""
 By GyllenhaalSP mar 2023 @ https://github.com/GyllenhaalSP.
"""
import os
import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class Mailer:
    def __init__(self, remitente, password):
        self.remitente = remitente
        self.password = password

    def enviar_email(self, destinatario, detalles_factura, n_fact, adjunto=None):
        # Define el mensaje del correo electrónico
        header = "Mail automático enviado por el sistema de facturación de Alimentación Chen S.L.\n\n"
        header += "Se adjunta la factura de la compra realizada en nuestra tienda.\n\n"
        header += "Gracias por su compra.\n\n"
        factura_monospace = f'<pre><font face="Courier New">{detalles_factura}</font></pre>'
        msg = MIMEMultipart()
        msg['Subject'] = f'Alimentación Chen - Factura número {n_fact}'
        msg['From'] = self.remitente
        msg['To'] = destinatario

        # Agregar el contenido del correo electrónico
        msg.attach(MIMEText(header, 'plain'))
        msg.attach(MIMEText(factura_monospace, 'html'))

        # Adjuntar el archivo PDF si se proporcionó
        if adjunto:
            with open(adjunto, "rb") as f:
                pdf = MIMEApplication(f.read(), _subtype="pdf")
                pdf.add_header('content-disposition', 'attachment', filename=os.path.basename(adjunto))
            msg.attach(pdf)

        try:
            # Crea la conexión con el servidor de correo electrónico y envía el mensaje
            server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            server.login(self.remitente, self.password)
            server.sendmail(self.remitente, [msg['To']], msg.as_string())
            server.quit()
        except Exception as e:
            with open("log.txt", "a") as log_file:
                log_file.write(f"Error al enviar correo electrónico: {e}\n")
