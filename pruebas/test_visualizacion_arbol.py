"""Comprueba las salidas de texto del árbol sintáctico."""

import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch

from algoritmos.cyk import construir_arbol_sintactico, cyk
from entrada_salida.lector_gramatica import leer_gramatica_desde_archivo
from entrada_salida.visualizacion_arbol import arbol_a_corchetes, arbol_a_texto
from entrada_salida.visualizacion_arbol import arbol_a_dot, buscar_ejecutable_dot, exportar_arbol_imagen
from modelos.nodo_arbol import NodoArbol
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

    def test_dot_y_escape(self) -> None:
        texto = arbol_a_dot(self.arbol)
        self.assertIn("digraph ArbolSintactico", texto)
        self.assertIn('ordering="out"', texto)
        self.assertEqual(texto.count("[label="), self.arbol.contar_nodos())
        self.assertEqual(texto.count(" -> "), self.arbol.contar_nodos() - 1)
        self.assertIn(r'label="\"\\"', arbol_a_dot(NodoArbol('"\\')))

    @unittest.skipUnless(buscar_ejecutable_dot(), "Graphviz no está instalado")
    def test_exportar_png(self) -> None:
        with tempfile.TemporaryDirectory() as carpeta:
            ruta = Path(carpeta) / "subcarpeta" / "arbol"
            imagen = exportar_arbol_imagen(self.arbol, ruta)
            self.assertTrue(ruta.with_suffix(".dot").exists())
            self.assertTrue(imagen.read_bytes().startswith(b"\x89PNG\r\n\x1a\n"))

    def test_sin_graphviz(self) -> None:
        with tempfile.TemporaryDirectory() as carpeta:
            ruta = Path(carpeta) / "arbol"
            with patch("entrada_salida.visualizacion_arbol.buscar_ejecutable_dot", return_value=None):
                self.assertIsNone(exportar_arbol_imagen(self.arbol, ruta))
            self.assertEqual(ruta.with_suffix(".dot").read_text(encoding="utf-8"),
                             arbol_a_dot(self.arbol))
