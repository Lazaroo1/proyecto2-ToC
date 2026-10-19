"""Pruebas de los archivos de gramáticas de ejemplo (carpeta gramaticas/)."""

import unittest
from pathlib import Path

RUTA_GRAMATICAS = Path(__file__).resolve().parent.parent / "gramaticas"

ARCHIVOS_ESPERADOS = (
    "ingles.txt",
    "1.txt",
    "1-cnf.txt",
    "expresiones_recursiva.txt",
    "hopcroft_epsilon.txt",
    "hopcroft_unitarias.txt",
    "inutiles.txt",
    "anbn.txt",
)

# Copias exactas de los archivos que entregó el catedrático.
CONTENIDO_1_TXT = """E -> T X
X -> + T X | e
T -> F Y
Y -> * F Y | e
F -> ( E ) | id
"""

CONTENIDO_1_CNF_TXT = """E -> T X | F Y | L Z | id
X -> P W | P T
T -> F Y | L Z | id
Y -> M V | M F
F -> L Z | id
Z -> E R
W -> T X
V -> F Y
L -> (
R -> )
P -> +
M -> *
"""


def leer_archivo_de_gramatica(nombre_archivo: str) -> str:
    """Devuelve el contenido de un archivo de gramaticas/ con saltos de línea normalizados."""
    return (RUTA_GRAMATICAS / nombre_archivo).read_text(encoding="utf-8-sig")


class PruebaArchivosGramaticas(unittest.TestCase):
    """Verifica que las gramáticas de ejemplo existan y tengan el formato acordado."""

    def test_existen_todos_los_archivos_y_no_estan_vacios(self) -> None:
        for nombre_archivo in ARCHIVOS_ESPERADOS:
            with self.subTest(archivo=nombre_archivo):
                ruta_archivo = RUTA_GRAMATICAS / nombre_archivo
                self.assertTrue(ruta_archivo.is_file(), f"Falta {nombre_archivo}")
                self.assertTrue(leer_archivo_de_gramatica(nombre_archivo).strip())

    def test_cada_produccion_tiene_flecha(self) -> None:
        for nombre_archivo in ARCHIVOS_ESPERADOS:
            for numero_linea, linea in enumerate(
                leer_archivo_de_gramatica(nombre_archivo).splitlines(), start=1
            ):
                linea_limpia = linea.strip()
                if not linea_limpia or linea_limpia.startswith("#"):
                    continue
                with self.subTest(archivo=nombre_archivo, linea=numero_linea):
                    self.assertIn("->", linea_limpia)

    def test_1_txt_es_copia_exacta_del_catedratico(self) -> None:
        self.assertEqual(leer_archivo_de_gramatica("1.txt"), CONTENIDO_1_TXT)

    def test_1_cnf_txt_es_copia_exacta_del_catedratico(self) -> None:
        self.assertEqual(leer_archivo_de_gramatica("1-cnf.txt"), CONTENIDO_1_CNF_TXT)


if __name__ == "__main__":
    unittest.main()
