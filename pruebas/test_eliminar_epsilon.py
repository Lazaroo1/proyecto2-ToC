"""Pruebas del paso 1: anulables y eliminación de producciones ε."""

import unittest
from pathlib import Path

from algoritmos.eliminar_epsilon import calcular_anulables
from entrada_salida.lector_gramatica import leer_gramatica_desde_archivo, leer_gramatica_desde_texto
from modelos.gramatica import Gramatica

RUTA_GRAMATICAS = Path(__file__).resolve().parent.parent / "gramaticas"


def leer_gramatica_de_ejemplo(nombre_archivo: str) -> Gramatica:
    """Lee una gramática de la carpeta gramaticas/."""
    return leer_gramatica_desde_archivo(RUTA_GRAMATICAS / nombre_archivo)


class PruebaCalcularAnulables(unittest.TestCase):
    """Verifica el cálculo de variables anulables (punto fijo)."""

    def test_gramatica_uno(self) -> None:
        self.assertEqual(calcular_anulables(leer_gramatica_de_ejemplo("1.txt")), {"X", "Y"})

    def test_ejemplo_del_libro(self) -> None:
        self.assertEqual(
            calcular_anulables(leer_gramatica_de_ejemplo("hopcroft_epsilon.txt")), {"S", "A", "B"}
        )

    def test_anbn(self) -> None:
        self.assertEqual(calcular_anulables(leer_gramatica_de_ejemplo("anbn.txt")), {"S"})

    def test_gramatica_del_ingles_no_tiene_anulables(self) -> None:
        self.assertEqual(calcular_anulables(leer_gramatica_de_ejemplo("ingles.txt")), set())

    def test_anulable_indirecto(self) -> None:
        gramatica = leer_gramatica_desde_texto("S -> A B c | A B\nA -> e\nB -> A A")
        self.assertEqual(calcular_anulables(gramatica), {"S", "A", "B"})

    def test_un_terminal_nunca_es_anulable(self) -> None:
        gramatica = leer_gramatica_de_ejemplo("1.txt")
        anulables = calcular_anulables(gramatica)
        self.assertTrue(anulables.isdisjoint(gramatica.terminales))


if __name__ == "__main__":
    unittest.main()
