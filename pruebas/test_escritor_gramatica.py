"""Pruebas del escritor de gramáticas (Gramatica -> texto/archivo)."""

import tempfile
import unittest
from pathlib import Path

from entrada_salida.escritor_gramatica import (
    describir_gramatica,
    gramatica_a_texto,
    guardar_gramatica_en_archivo,
)
from entrada_salida.lector_gramatica import leer_gramatica_desde_archivo, leer_gramatica_desde_texto

RUTA_GRAMATICAS = Path(__file__).resolve().parent.parent / "gramaticas"


class PruebaEscritorGramatica(unittest.TestCase):
    """Verifica el formato de salida y la ida y vuelta con el lector."""

    def test_reescribir_1_cnf_da_el_mismo_texto(self) -> None:
        ruta_1_cnf = RUTA_GRAMATICAS / "1-cnf.txt"
        texto_original = ruta_1_cnf.read_text(encoding="utf-8-sig").rstrip("\n")
        self.assertEqual(gramatica_a_texto(leer_gramatica_desde_archivo(ruta_1_cnf)), texto_original)

    def test_epsilon_se_escribe_con_letra_griega(self) -> None:
        texto = gramatica_a_texto(leer_gramatica_desde_archivo(RUTA_GRAMATICAS / "1.txt"))
        self.assertIn("X -> + T X | ε", texto.splitlines())

    def test_no_escribe_variables_sin_producciones(self) -> None:
        texto = gramatica_a_texto(leer_gramatica_desde_archivo(RUTA_GRAMATICAS / "inutiles.txt"))
        self.assertEqual(texto, "S -> A B | a\nA -> b")

    def test_ida_y_vuelta_con_todas_las_gramaticas(self) -> None:
        for ruta_archivo in sorted(RUTA_GRAMATICAS.glob("*.txt")):
            with self.subTest(archivo=ruta_archivo.name):
                gramatica_original = leer_gramatica_desde_archivo(ruta_archivo)
                gramatica_releida = leer_gramatica_desde_texto(gramatica_a_texto(gramatica_original))
                self.assertEqual(gramatica_releida, gramatica_original)
                self.assertEqual(gramatica_releida.variables[0], gramatica_original.simbolo_inicial)

    def test_describir_gramatica_uno(self) -> None:
        gramatica = leer_gramatica_desde_archivo(RUTA_GRAMATICAS / "1.txt")
        self.assertEqual(
            describir_gramatica(gramatica),
            "Símbolo inicial: E | Variables (5): E, X, T, Y, F | "
            "Terminales (5): +, *, (, ), id | Producciones: 8",
        )

    def test_guardar_y_volver_a_leer(self) -> None:
        gramatica = leer_gramatica_desde_archivo(RUTA_GRAMATICAS / "ingles.txt")
        with tempfile.TemporaryDirectory() as carpeta_temporal:
            ruta_destino = Path(carpeta_temporal) / "subcarpeta" / "ingles_copia.txt"
            guardar_gramatica_en_archivo(gramatica, ruta_destino)
            gramatica_releida = leer_gramatica_desde_archivo(ruta_destino)
        self.assertEqual(gramatica_releida, gramatica)


if __name__ == "__main__":
    unittest.main()
