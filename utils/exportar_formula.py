import pandas as pd
from openpyxl import Workbook
from openpyxl.utils import get_column_letter
from io import BytesIO

def exportar_formula_excel(df: pd.DataFrame, nombre_formula: str) -> BytesIO:
    wb = Workbook()
    ws = wb.active
    ws.title = "Fórmula"

    # Columnas que interesan
    columnas_base = ["Materia Prima", "%"]
    columnas_tecnicas = [col for col in df.columns if col not in columnas_base and col != "Precio €/kg"]
    columnas_final = columnas_base + columnas_tecnicas

    # Escribir encabezados
    for col_idx, col_name in enumerate(columnas_final, start=1):
        ws.cell(row=1, column=col_idx, value=col_name)

    # Escribir cada fila con fórmulas en columnas técnicas
    for row_idx, row in enumerate(df.itertuples(index=False), start=2):
        materia = getattr(row, "Materia Prima", "")
        porcentaje = getattr(row, "%", 0)
        ws.cell(row=row_idx, column=1, value=materia)
        ws.cell(row=row_idx, column=2, value=porcentaje)

        for col_offset, col in enumerate(columnas_tecnicas, start=3):
            letra = get_column_letter(col_offset)
            val = getattr(row, col, 0)
            ws.cell(row=row_idx, column=col_offset, value=f"={val}*$B{row_idx}/100")

    fila_total = df.shape[0] + 2

    # Calcular totales con SUMPRODUCT
    for col_offset, col in enumerate(columnas_tecnicas, start=3):
        letra = get_column_letter(col_offset)
        ws.cell(row=fila_total, column=col_offset,
                value=f"=SUMPRODUCT({letra}2:{letra}{fila_total - 1})")

    # Ajustar ancho de columnas
    for col in ws.columns:
        max_len = max(len(str(cell.value)) if cell.value else 0 for cell in col)
        ws.column_dimensions[col[0].column_letter].width = max(max_len + 2, 10)

    output = BytesIO()
    wb.save(output)
    output.seek(0)
    return output



