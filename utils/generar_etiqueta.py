from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from datetime import datetime

def generar_etiqueta(nombre: str, fecha: str, qr_img: Image.Image) -> BytesIO:
    ancho, alto = 472, 283  # 5x3 cm a 240 dpi
    etiqueta = Image.new("RGB", (ancho, alto), "white")
    draw = ImageDraw.Draw(etiqueta)

    try:
        fuente = ImageFont.truetype("arial.ttf", 20)
    except:
        fuente = ImageFont.load_default()

    draw.text((10, 10), f"Nombre: {nombre}", font=fuente, fill="black")
    draw.text((10, 40), f"Fecha: {fecha}", font=fuente, fill="black")

    qr_img = qr_img.resize((100, 100))
    etiqueta.paste(qr_img, (ancho - 110, alto - 110))

    output = BytesIO()
    etiqueta.save(output, format="PDF")
    output.seek(0)
    return output
