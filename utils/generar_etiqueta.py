# ------------------------------------------------------------------------------
# FORMULATOR – Uso exclusivo de Iván Navarro
# Todos los derechos reservados © 2025
# Este archivo forma parte de un software no libre y no está autorizado su uso
# ni distribución sin consentimiento expreso y por escrito del autor.
# ------------------------------------------------------------------------------

from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

def generar_etiqueta(nombre: str, fecha: str, qr_img: Image.Image) -> BytesIO:
    """
    Genera una etiqueta PDF de 5x3 cm con nombre, fecha y QR en alta resolución.

    Args:
        nombre (str): Nombre de la fórmula.
        fecha (str): Fecha de creación (YYYY-MM-DD).
        qr_img (Image.Image): Imagen QR ya generada.

    Returns:
        BytesIO: Etiqueta en formato PDF lista para descargar.
    """
    # 🔍 Tamaño etiqueta en cm → px a 600 DPI
    dpi = 600
    cm_to_inches = 0.393701
    width_px = int(5 * cm_to_inches * dpi)   # ~1181 px
    height_px = int(3 * cm_to_inches * dpi)  # ~709 px

    # 🎨 Crear imagen blanca
    etiqueta = Image.new("RGB", (width_px, height_px), "white")
    draw = ImageDraw.Draw(etiqueta)

    # 🔤 Fuente
    try:
        font = ImageFont.truetype("arial.ttf", size=48)
    except:
        font = ImageFont.load_default()

    # 🖋️ Escribir nombre y fecha
    draw.text((50, 50), f"Nombre: {nombre}", font=font, fill="black")
    draw.text((50, 130), f"Fecha: {fecha}", font=font, fill="black")

    # 🧩 QR: tamaño y ubicación
    qr_size = 300
    qr_img = qr_img.resize((qr_size, qr_size), resample=Image.BICUBIC)
    etiqueta.paste(qr_img, (width_px - qr_size - 50, height_px - qr_size - 50))

    # 💾 Guardar como PDF
    output = BytesIO()
    etiqueta.save(output, format="PDF", resolution=dpi)
    output.seek(0)
    return output
