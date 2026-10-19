"""Comprueba las salidas de texto del árbol sintáctico."""

import unittest

from algoritmos.cyk import construir_arbol_sintactico, cyk
from entrada_salida.lector_gramatica import leer_gramatica_desde_archivo
from entrada_salida.visualizacion_arbol import arbol_a_corchetes, arbol_a_texto
from pruebas.test_arbol_sintactico import ARBOL_INGLES
from pruebas.test_cyk import RUTA_GRAMATICAS


class PruebaVisualizacionArbol(unittest.TestCase):
    """Verifica el formato exacto de ramas y corchetes."""

    def setUp(self) -> None:
        self.gramatica = leer_gramatica_desde_archivo(RUTA_GRAMATICAS / "ingles.txt")
        self.arbol = construir_arbol_sintactico(cyk(self.gramatica, ["he", "cooks"]), "S")

    def test_he_cooks(self) -> None:
        self.assertEqual(arbol_a_texto(self.arbol), "S\n├── NP\n│   └── he\n└── VP\n    └── cooks")
        self.assertEqual(arbol_a_corchetes(self.arbol), "[S [NP he] [VP cooks]]")

    def test_frase_del_enunciado(self) -> None:
        arbol = construir_arbol_sintactico(
            cyk(self.gramatica, "she eats a cake with a fork".split()), "S")
        self.assertEqual(arbol_a_corchetes(arbol), ARBOL_INGLES)
        self.assertEqual(len(arbol_a_texto(arbol).splitlines()), arbol.contar_nodos())
