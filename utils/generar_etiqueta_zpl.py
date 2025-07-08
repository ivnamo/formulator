# ------------------------------------------------------------------------------
# FORMULATOR – Uso exclusivo de Iván Navarro
# Todos los derechos reservados © 2025
# Este archivo forma parte de un software no libre y no está autorizado su uso
# ni distribución sin consentimiento expreso y por escrito del autor.
# ------------------------------------------------------------------------------

"""Funciones para generar etiquetas en formato ZPL para impresoras Zebra."""


def generar_etiqueta_zpl(nombre_formula: str, fecha: str, url: str) -> str:
    """Devuelve el contenido ZPL para una etiqueta.

    La etiqueta incluye el nombre de la fórmula, la fecha de creación y un
    código QR que apunta a la URL proporcionada.
    """
    zpl = f"""
^XA
^CF0,40
^FO20,20^FD{nombre_formula}^FS
^CF0,25
^FO20,70^FD{fecha}^FS
^FO20,110^BQN,2,6^FDLA,{url}^FS
^XZ
"""
    return zpl
