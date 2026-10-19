"""Pruebas de la Forma Normal de Chomsky: validación y conversión."""

import unittest
from pathlib import Path

from algoritmos.forma_normal_chomsky import (
    es_forma_normal_chomsky,
    obtener_producciones_fuera_de_cnf,
)
from entrada_salida.lector_gramatica import leer_gramatica_desde_archivo, leer_gramatica_desde_texto
from modelos.gramatica import Gramatica

RUTA_GRAMATICAS = Path(__file__).resolve().parent.parent / "gramaticas"


def leer_gramatica_de_ejemplo(nombre_archivo: str) -> Gramatica:
    """Lee una gramática de la carpeta gramaticas/."""
    return leer_gramatica_desde_archivo(RUTA_GRAMATICAS / nombre_archivo)


class PruebaValidarCnf(unittest.TestCase):
    """Verifica si una gramática ya está en CNF."""

    def test_gramaticas_que_ya_estan_en_cnf(self) -> None:
        for nombre_archivo in ("1-cnf.txt", "ingles.txt"):
            with self.subTest(archivo=nombre_archivo):
                gramatica = leer_gramatica_de_ejemplo(nombre_archivo)
                self.assertTrue(es_forma_normal_chomsky(gramatica))
                self.assertEqual(obtener_producciones_fuera_de_cnf(gramatica), [])

    def test_gramatica_uno_no_esta_en_cnf(self) -> None:
        gramatica = leer_gramatica_de_ejemplo("1.txt")
        producciones_invalidas = obtener_producciones_fuera_de_cnf(gramatica)
        self.assertFalse(es_forma_normal_chomsky(gramatica))
        self.assertIn(("X", ("+", "T", "X")), producciones_invalidas)
        self.assertIn(("X", ()), producciones_invalidas)
        self.assertIn(("F", ("(", "E", ")")), producciones_invalidas)
        self.assertNotIn(("F", ("id",)), producciones_invalidas)
        self.assertNotIn(("E", ("T", "X")), producciones_invalidas)

    def test_cada_tipo_de_produccion_invalida(self) -> None:
        casos = {
            "mixta": "A -> a B\nB -> b",
            "unitaria": "A -> B\nB -> b",
            "larga": "A -> B C D\nB -> b\nC -> c\nD -> d",
            "epsilon": "A -> e",
        }
        for tipo_produccion, texto_gramatica in casos.items():
            with self.subTest(tipo=tipo_produccion):
                gramatica = leer_gramatica_desde_texto(texto_gramatica)
                self.assertFalse(es_forma_normal_chomsky(gramatica))
                self.assertEqual(obtener_producciones_fuera_de_cnf(gramatica)[0][0], "A")


if __name__ == "__main__":
    unittest.main()
