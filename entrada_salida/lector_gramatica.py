"""Lectura de gramáticas desde texto o desde archivos .txt.

Formato aceptado (ver README):

- Una producción por línea: ``CABEZA -> cuerpo1 | cuerpo2 | ...`` (también ``→``).
- Los símbolos se separan con espacios; un terminal puede tener varias letras.
- ``e`` o ``ε`` representan la cadena vacía.
- Variable: todo símbolo que aparece como cabeza o que empieza con mayúscula.
- El símbolo inicial es la cabeza de la primera producción.
- Las líneas vacías y las que empiezan con ``#`` se ignoran.
"""

from __future__ import annotations

from pathlib import Path
from typing import NamedTuple

from modelos.gramatica import Cuerpo, Gramatica

SIMBOLOS_EPSILON: tuple[str, ...] = ("e", "ε")
FLECHAS: tuple[str, ...] = ("->", "→")
SEPARADOR_DE_ALTERNATIVAS = "|"
INICIO_DE_COMENTARIO = "#"


class ErrorFormatoGramatica(ValueError):
    """Error en el formato del texto de una gramática.

    Atributos:
        numero_linea: línea (desde 1) donde está el error, o None si es de todo el texto.
    """

    def __init__(self, descripcion: str, numero_linea: int | None = None) -> None:
        self.numero_linea = numero_linea
        mensaje = f"Línea {numero_linea}: {descripcion}" if numero_linea else descripcion
        super().__init__(mensaje)


class _LineaDeProducciones(NamedTuple):
    """Producciones leídas de una línea del texto."""

    numero_linea: int
    cabeza: str
    cuerpos: list[Cuerpo]


def leer_gramatica_desde_texto(texto: str) -> Gramatica:
    """Convierte el texto de una gramática en un objeto Gramatica.

    Parámetros:
        texto: contenido en el formato descrito en el docstring del módulo.

    Retorna:
        La gramática leída. Las cabezas quedan como variables en orden de
        aparición y después se agregan, sin producciones, los símbolos en
        mayúscula que no son cabeza de ninguna producción.

    Lanza:
        ErrorFormatoGramatica: si el texto no respeta el formato.
    """
    lineas_leidas: list[_LineaDeProducciones] = []
    for numero_linea, linea_original in enumerate(texto.splitlines(), start=1):
        linea = linea_original.strip()
        if not linea or linea.startswith(INICIO_DE_COMENTARIO):
            continue
        cabeza, textos_alternativas = _separar_cabeza_y_alternativas(linea, numero_linea)
        cuerpos = [
            _convertir_alternativa_en_cuerpo(texto_alternativa, numero_linea)
            for texto_alternativa in textos_alternativas
        ]
        lineas_leidas.append(_LineaDeProducciones(numero_linea, cabeza, cuerpos))

    if not lineas_leidas:
        raise ErrorFormatoGramatica("la gramática no tiene producciones.")

    gramatica = Gramatica(lineas_leidas[0].cabeza)
    for linea_leida in lineas_leidas:
        gramatica.agregar_variable(linea_leida.cabeza)
    for linea_leida in lineas_leidas:
        for cuerpo in linea_leida.cuerpos:
            gramatica.agregar_produccion(linea_leida.cabeza, cuerpo)

    # Un símbolo en mayúscula es variable aunque no tenga producciones (ej. B en S -> A B | a).
    for linea_leida in lineas_leidas:
        for cuerpo in linea_leida.cuerpos:
            for simbolo in cuerpo:
                if simbolo[0].isupper() and not gramatica.es_variable(simbolo):
                    gramatica.agregar_variable(simbolo)
    return gramatica


def leer_gramatica_desde_archivo(ruta_archivo: str | Path) -> Gramatica:
    """Lee una gramática desde un archivo de texto.

    Se usa la codificación "utf-8-sig" para tolerar el BOM que agrega el Bloc de notas.

    Parámetros:
        ruta_archivo: ruta del archivo .txt.

    Retorna:
        La gramática leída.

    Lanza:
        FileNotFoundError: si el archivo no existe.
        ErrorFormatoGramatica: si el contenido no respeta el formato.
    """
    texto = Path(ruta_archivo).read_text(encoding="utf-8-sig")
    return leer_gramatica_desde_texto(texto)


def _separar_cabeza_y_alternativas(linea: str, numero_linea: int) -> tuple[str, list[str]]:
    """Separa "CABEZA -> a | b" en la cabeza y los textos de cada alternativa."""
    flecha_encontrada = next((flecha for flecha in FLECHAS if flecha in linea), None)
    if flecha_encontrada is None:
        raise ErrorFormatoGramatica("falta la flecha '->' entre la cabeza y los cuerpos.", numero_linea)

    texto_cabeza, texto_cuerpos = linea.split(flecha_encontrada, 1)
    if any(flecha in texto_cuerpos for flecha in FLECHAS):
        raise ErrorFormatoGramatica("hay más de una flecha en la misma línea.", numero_linea)

    cabeza = texto_cabeza.strip()
    if not cabeza:
        raise ErrorFormatoGramatica("la cabeza de la producción está vacía.", numero_linea)
    if len(cabeza.split()) > 1:
        raise ErrorFormatoGramatica(
            f"la cabeza '{cabeza}' debe ser una sola variable, sin espacios.", numero_linea
        )
    if cabeza in SIMBOLOS_EPSILON:
        raise ErrorFormatoGramatica(
            f"'{cabeza}' representa la cadena vacía y no puede ser cabeza.", numero_linea
        )
    return cabeza, texto_cuerpos.split(SEPARADOR_DE_ALTERNATIVAS)


def _convertir_alternativa_en_cuerpo(texto_alternativa: str, numero_linea: int) -> Cuerpo:
    """Convierte el texto de una alternativa en un cuerpo; "e" o "ε" solos son la tupla vacía."""
    simbolos = texto_alternativa.split()
    if not simbolos:
        raise ErrorFormatoGramatica(
            "hay una alternativa vacía; para la cadena vacía escribe 'e' o 'ε'.", numero_linea
        )
    if len(simbolos) == 1 and simbolos[0] in SIMBOLOS_EPSILON:
        return ()
    if any(simbolo in SIMBOLOS_EPSILON for simbolo in simbolos):
        raise ErrorFormatoGramatica(
            "'e'/'ε' (cadena vacía) no puede ir junto a otros símbolos.", numero_linea
        )
    return tuple(simbolos)
