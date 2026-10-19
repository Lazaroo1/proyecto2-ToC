"""Pruebas de tokenización con los vocabularios reales."""

import unittest
from pathlib import Path

from entrada_salida.lector_gramatica import leer_gramatica_desde_archivo
from entrada_salida.tokenizador import encontrar_tokens_desconocidos, tokenizar_frase

RUTA_GRAMATICAS = Path(__file__).resolve().parent.parent / "gramaticas"


class PruebaTokenizador(unittest.TestCase):
    """Comprueba normalización, segmentación y palabras desconocidas."""

    def test_vocabularios_reales(self) -> None:
        casos = [
            ("ingles.txt", "She eats a cake with a fork", "she eats a cake with a fork"),
            ("ingles.txt", "The cat drinks the beer.", "the cat drinks the beer"),
            ("ingles.txt", "  he   COOKS  ", "he cooks"),
            ("ingles.txt", "she eats pizza", "she eats pizza"),
            ("ingles.txt", "she eats athe cake", "she eats athe cake"),
            ("ingles.txt", "", ""),
            ("ingles.txt", "...", ""),
            ("1.txt", "(id*id)+id", "( id * id ) + id"),
            ("1.txt", "( id * id ) + id", "( id * id ) + id"),
            ("1.txt", "idid", "idid"),
            ("anbn.txt", "aabb", "a a b b"),
        ]
        for archivo, frase, esperado in casos:
            with self.subTest(archivo=archivo, frase=frase):
                terminales = leer_gramatica_desde_archivo(RUTA_GRAMATICAS / archivo).terminales
                self.assertEqual(tokenizar_frase(frase, terminales), esperado.split())
        self.assertEqual(encontrar_tokens_desconocidos(["pizza", "he", "pizza"], ["he"]),
                         ["pizza"])

    def test_segmentacion_completa_y_puntuacion_terminal(self) -> None:
        self.assertEqual(tokenizar_frase("abc!", ["ab", "a", "bc", "!"]), ["a", "bc", "!"])
        self.assertEqual(tokenizar_frase("!", ["!"]), ["!"])
        self.assertEqual(tokenizar_frase("XYZ", []), ["xyz"])
