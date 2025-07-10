# ------------------------------------------------------------------------------
# FORMULATOR – Uso exclusivo de Iván Navarro
# Todos los derechos reservados © 2025
# Este archivo forma parte de un software no libre y no está autorizado su uso
# ni distribución sin consentimiento expreso y por escrito del autor.
# ------------------------------------------------------------------------------

import pandas as pd
from openpyxl import Workbook
from openpyxl.utils import get_column_letter
from io import BytesIO

def exportar_formula_excel(df: pd.DataFrame, nombre_formula: str) -> BytesIO:
    """
    Exporta una fórmula a Excel con subtotal y composición técnica calculada.

    Args:
        df (pd.DataFrame): DataFrame con columnas 'Materia Prima', 'Precio €/kg', '%', parámetros técnicos.
        nombre_formula (str): Nombre para el archivo.

    Returns:
        BytesIO: Excel listo para descargar.
    """
    wb = Workbook()
    ws = wb.active
    ws.title = "Fórmula"

    # Columnas base + técnicas + subtotal
    columnas_base = ["Materia Prima", "Precio €/kg", "%"]
    columnas_tecnicas = [col for col in df.columns if col not in columnas_base]
    columnas_final = columnas_base + columnas_tecnicas + ["Subtotal €/kg"]
    ws.append(columnas_final)

    for i, row in enumerate(df.itertuples(index=False), start=2):
        fila = [row._asdict().get(col, "") for col in columnas_base]

        # columnas técnicas con fórmula: =valor * $C2 / 100
        for j, col in enumerate(columnas_tecnicas, start=4):
            letra_col = get_column_letter(j)
            fila.append(f"={letra_col}{i}*$C{i}/100")

        # subtotal: =B2*C2/100
        fila.append(f"=B{i}*C{i}/100")
        ws.append(fila)

    fila_total = len(df) + 2

    # Total €/kg
    col_subtotal = len(columnas_final)
    letra_subtotal = get_column_letter(col_subtotal)
    ws[f"A{fila_total}"] = "TOTAL €/kg:"
    ws[f"{letra_subtotal}{fila_total}"] = f"=SUM({letra_subtotal}2:{letra_subtotal}{fila_total - 1})"

    # Totales por cada columna técnica
    for idx, col in enumerate(columnas_tecnicas, start=4):
        letra = get_column_letter(idx)
        ws[f"{letra}{fila_total}"] = f"=SUM({letra}2:{letra}{fila_total - 1})"

    # Ajustar ancho de columnas
    for col in ws.columns:
        max_len = max(len(str(cell.value)) if cell.value else 0 for cell in col)
        ws.column_dimensions[col[0].column_letter].width = max(max_len + 2, 10)

    output = BytesIO()
    wb.save(output)
    output.seek(0)
    return output


