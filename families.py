# families.py

from collections import defaultdict

def obtener_familias_parametros():
    return {
        "Macronutriente": ["Ntotal", "Norg", "Nnitr", "Nure", "Namo", "K2O", "P2O5"],
        "Secundario": ["CaO", "MgO", "SO3"],
        "Micronutriente": ["Zn", "Mn", "Fe", "Cu", "B", "Mo", "Co", "SiO2"],
        "Fracción Orgánica": [
            "Mseca", "Morg", "Corg", "Extracto Húmico total",
            "Acidos fulvicos", "Acidos húmicos", "Extracto de Algas", "Polisacaridos"
        ],
        "Aminoácidos": ["Sum AA totales", "Sum AA libres"],
        "Aminograma": [
            "Ac aspartico", "Ac glutamico", "Alanina", "Glicina", "Histidina",
            "Isoleucina", "Leucina", "Lisina", "Serina", "Tirosina", "Treonina",
            "Valina", "Arginina", "Fenilalanina", "Metionina", "Prolina",
            "Hidroxiprolina", "Triptofano"
        ],
        "Metales pesados": ["As", "Hg", "Pb", "Cd", "Cr", "Ni"]
    }
