"""Escritura de gramáticas: lo inverso del lector (Gramatica -> texto o archivo).

El texto que se produce usa el mismo formato que acepta el lector, así que una
gramática escrita se puede volver a leer sin cambios.
"""

from __future__ import annotations

from pathlib import Path

from modelos.gramatica import Gramatica

SIMBOLO_EPSILON_SALIDA = "ε"


def gramatica_a_texto(gramatica: Gramatica) -> str:
    """Convierte una gramática al formato "CABEZA -> s1 s2 | s3".

    Se escribe una línea por variable (en orden) que tenga al menos una
    producción; el cuerpo vacío se escribe como ε.

    Parámetros:
        gramatica: gramática a convertir.

    Retorna:
        Las líneas unidas con saltos de línea, sin salto al final.
    """
    lineas: list[str] = []
    for variable in gramatica.variables:
        cuerpos = gramatica.obtener_producciones(variable)
        if not cuerpos:
            continue
        alternativas = [" ".join(cuerpo) if cuerpo else SIMBOLO_EPSILON_SALIDA for cuerpo in cuerpos]
        lineas.append(f"{variable} -> {' | '.join(alternativas)}")
    return "\n".join(lineas)


def describir_gramatica(gramatica: Gramatica) -> str:
    """Resume una gramática en una sola línea.

    Ejemplo con 1.txt:
    "Símbolo inicial: E | Variables (5): E, X, T, Y, F | Terminales (5): +, *, (, ), id | Producciones: 8"

    Parámetros:
        gramatica: gramática a describir.

    Retorna:
        Símbolo inicial, variables, terminales y cantidad de producciones.
    """
    variables = gramatica.variables
    terminales = gramatica.terminales
    return (
        f"Símbolo inicial: {gramatica.simbolo_inicial} | "
        f"Variables ({len(variables)}): {', '.join(variables)} | "
        f"Terminales ({len(terminales)}): {', '.join(terminales) or 'ninguno'} | "
        f"Producciones: {gramatica.contar_producciones()}"
    )


def guardar_gramatica_en_archivo(gramatica: Gramatica, ruta_archivo: str | Path) -> None:
    """Guarda la gramática en un archivo de texto (UTF-8), creando las carpetas que falten.

    Parámetros:
        gramatica: gramática a guardar.
        ruta_archivo: ruta del archivo de destino.
    """
    ruta_destino = Path(ruta_archivo)
    ruta_destino.parent.mkdir(parents=True, exist_ok=True)
    ruta_destino.write_text(gramatica_a_texto(gramatica) + "\n", encoding="utf-8")
