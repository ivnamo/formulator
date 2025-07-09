# ------------------------------------------------------------------------------
# FORMULATOR – Uso exclusivo de Iván Navarro
# Todos los derechos reservados © 2025
# Este archivo forma parte de un software no libre y no está autorizado su uso
# ni distribución sin consentimiento expreso y por escrito del autor.
# ------------------------------------------------------------------------------

import qrcode
from io import BytesIO
from PIL import Image

def generar_qr(url: str) -> Image.Image:
    """
    Genera una imagen QR a partir de una URL.

    Args:
        url (str): URL que se quiere codificar.

    Returns:
        PIL.Image.Image: Imagen QR generada.
    """
    qr = qrcode.make(url)
    img_buffer = BytesIO()
    qr.save(img_buffer, format='PNG')
    img_buffer.seek(0)
    return Image.open(img_buffer)
