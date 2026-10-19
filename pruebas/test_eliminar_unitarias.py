"""Pruebas del paso 2: parejas unitarias y eliminación de producciones unitarias."""

import unittest
from pathlib import Path

from algoritmos.eliminar_epsilon import eliminar_producciones_epsilon
from algoritmos.eliminar_unitarias import (
    calcular_parejas_unitarias,
    eliminar_producciones_unitarias,
    es_produccion_unitaria,
)
from entrada_salida.escritor_gramatica import gramatica_a_texto
from entrada_salida.lector_gramatica import leer_gramatica_desde_archivo, leer_gramatica_desde_texto
from modelos.gramatica import Gramatica

RUTA_GRAMATICAS = Path(__file__).resolve().parent.parent / "gramaticas"


def leer_gramatica_de_ejemplo(nombre_archivo: str) -> Gramatica:
    """Lee una gramática de la carpeta gramaticas/."""
    return leer_gramatica_desde_archivo(RUTA_GRAMATICAS / nombre_archivo)


class PruebaEsProduccionUnitaria(unittest.TestCase):
    """Distingue producciones unitarias de las demás."""

    def test_distingue_unitarias(self) -> None:
        gramatica = leer_gramatica_de_ejemplo("hopcroft_unitarias.txt")
        self.assertTrue(es_produccion_unitaria(gramatica, ("T",)))
        self.assertFalse(es_produccion_unitaria(gramatica, ("a",)))
        self.assertFalse(es_produccion_unitaria(gramatica, ("E", "+", "T")))
        self.assertFalse(es_produccion_unitaria(gramatica, ()))


class PruebaGramaticaUno(unittest.TestCase):
    """Paso 2 aplicado a la salida del paso 1 de 1.txt (PDF, página 2)."""

    def setUp(self) -> None:
        self.gramatica_sin_epsilon = eliminar_producciones_epsilon(leer_gramatica_de_ejemplo("1.txt"))

    def test_parejas_unitarias(self) -> None:
        self.assertEqual(
            calcular_parejas_unitarias(self.gramatica_sin_epsilon),
            [("E", "E"), ("E", "T"), ("E", "F"), ("X", "X"), ("T", "T"), ("T", "F"),
             ("Y", "Y"), ("F", "F")],
        )

    def test_nueva_gramatica_como_en_el_pdf(self) -> None:
        self.assertEqual(
            gramatica_a_texto(eliminar_producciones_unitarias(self.gramatica_sin_epsilon)),
            "E -> T X | F Y | ( E ) | id\n"
            "X -> + T X | + T\n"
            "T -> F Y | ( E ) | id\n"
            "Y -> * F Y | * F\n"
            "F -> ( E ) | id",
        )


class PruebaEjemploDelLibro(unittest.TestCase):
    """Ejemplo del libro incluido en el PDF (páginas 1 y 3)."""

    def setUp(self) -> None:
        self.gramatica = leer_gramatica_de_ejemplo("hopcroft_unitarias.txt")

    def test_parejas_unitarias(self) -> None:
        self.assertEqual(
            calcular_parejas_unitarias(self.gramatica),
            [("E", "E"), ("E", "T"), ("E", "F"), ("E", "I"), ("T", "T"), ("T", "F"),
             ("T", "I"), ("F", "F"), ("F", "I"), ("I", "I")],
        )

    def test_producciones_resultantes_como_en_la_tabla_del_pdf(self) -> None:
        self.assertEqual(
            gramatica_a_texto(eliminar_producciones_unitarias(self.gramatica)),
            "E -> E + T | T * F | ( E ) | a | b | I a | I b | I 0 | I 1\n"
            "T -> T * F | ( E ) | a | b | I a | I b | I 0 | I 1\n"
            "F -> ( E ) | a | b | I a | I b | I 0 | I 1\n"
            "I -> a | b | I a | I b | I 0 | I 1",
        )


class PruebaCasosBorde(unittest.TestCase):
    """Ciclos, gramáticas sin unitarias e inmutabilidad."""

    def test_ciclo_de_unitarias_termina(self) -> None:
        gramatica = leer_gramatica_desde_texto("A -> B | a\nB -> A | b")
        self.assertEqual(
            calcular_parejas_unitarias(gramatica), [("A", "A"), ("A", "B"), ("B", "B"), ("B", "A")]
        )
        self.assertEqual(
            gramatica_a_texto(eliminar_producciones_unitarias(gramatica)), "A -> a | b\nB -> b | a"
        )

    def test_gramatica_del_ingles_queda_igual(self) -> None:
        gramatica_ingles = leer_gramatica_de_ejemplo("ingles.txt")
        resultado = eliminar_producciones_unitarias(gramatica_ingles)
        self.assertEqual(gramatica_a_texto(resultado), gramatica_a_texto(gramatica_ingles))

    def test_no_modifica_la_gramatica_original(self) -> None:
        gramatica = leer_gramatica_de_ejemplo("hopcroft_unitarias.txt")
        copia_antes = gramatica.copiar()
        eliminar_producciones_unitarias(gramatica)
        self.assertEqual(gramatica_a_texto(gramatica), gramatica_a_texto(copia_antes))


if __name__ == "__main__":
    unittest.main()
