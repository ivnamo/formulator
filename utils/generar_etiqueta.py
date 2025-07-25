# ------------------------------------------------------------------------------
# FORMULATOR – Uso exclusivo de Iván Navarro
# Todos los derechos reservados © 2025
# Este archivo forma parte de un software no libre y no está autorizado su uso
# ni distribución sin consentimiento expreso y por escrito del autor.
# ------------------------------------------------------------------------------

from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from io import BytesIO
from PIL import Image

def generar_etiqueta(nombre: str, fecha: str, qr_img: Image.Image, codigo: str = "") -> BytesIO:
    """
    Genera una etiqueta PDF de 5x3 cm con nombre, código y fecha, junto con código QR.
    """
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=(5 * cm, 3 * cm))  # 5x3 cm

    # Texto (solo valores, sin etiquetas)
    c.setFont("Helvetica-Bold", 8)
    y_pos = 75
    if nombre:
        c.drawString(10, y_pos, nombre)
        y_pos -= 15
    if codigo:
        c.drawString(10, y_pos, codigo)
        y_pos -= 15
    if fecha:
        c.drawString(10, y_pos, fecha)

    # QR como ImageReader
    qr_reader = ImageReader(qr_img)
    c.drawImage(qr_reader, x=5 * cm - 60, y=5, width=55, height=55, mask='auto')

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer
