"""Pruebas del paso 1: anulables y eliminación de producciones ε."""

import unittest
from pathlib import Path

from algoritmos.eliminar_epsilon import calcular_anulables, eliminar_producciones_epsilon
from entrada_salida.escritor_gramatica import gramatica_a_texto
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


class PruebaEliminarProduccionesEpsilon(unittest.TestCase):
    """Verifica el paso 1 contra los resultados del PDF del catedrático."""

    def test_gramatica_uno_como_en_el_pdf(self) -> None:
        resultado = eliminar_producciones_epsilon(leer_gramatica_de_ejemplo("1.txt"))
        self.assertEqual(
            gramatica_a_texto(resultado),
            "E -> T X | T\n"
            "X -> + T X | + T\n"
            "T -> F Y | F\n"
            "Y -> * F Y | * F\n"
            "F -> ( E ) | id",
        )

    def test_ejemplo_del_libro_como_en_el_pdf(self) -> None:
        resultado = eliminar_producciones_epsilon(leer_gramatica_de_ejemplo("hopcroft_epsilon.txt"))
        self.assertEqual(
            gramatica_a_texto(resultado),
            "S -> A B | A | B\n"
            "A -> a A A | a A | a\n"
            "B -> b B B | b B | b",
        )

    def test_anbn(self) -> None:
        resultado = eliminar_producciones_epsilon(leer_gramatica_de_ejemplo("anbn.txt"))
        self.assertEqual(gramatica_a_texto(resultado), "S -> a S b | a b")

    def test_gramatica_sin_anulables_queda_igual(self) -> None:
        gramatica_ingles = leer_gramatica_de_ejemplo("ingles.txt")
        resultado = eliminar_producciones_epsilon(gramatica_ingles)
        self.assertEqual(resultado, gramatica_ingles)
        self.assertEqual(gramatica_a_texto(resultado), gramatica_a_texto(gramatica_ingles))

    def test_no_quedan_cuerpos_vacios(self) -> None:
        for nombre_archivo in ("1.txt", "hopcroft_epsilon.txt", "anbn.txt"):
            resultado = eliminar_producciones_epsilon(leer_gramatica_de_ejemplo(nombre_archivo))
            for variable in resultado.variables:
                with self.subTest(archivo=nombre_archivo, variable=variable):
                    self.assertNotIn((), resultado.obtener_producciones(variable))

    def test_conserva_las_variables_y_su_orden(self) -> None:
        gramatica = leer_gramatica_desde_texto("S -> a B\nB -> e")
        resultado = eliminar_producciones_epsilon(gramatica)
        self.assertEqual(resultado.variables, ["S", "B"])
        self.assertEqual(resultado.obtener_producciones("S"), [("a", "B"), ("a",)])
        self.assertEqual(resultado.obtener_producciones("B"), [])

    def test_no_modifica_la_gramatica_original(self) -> None:
        gramatica = leer_gramatica_de_ejemplo("1.txt")
        copia_antes = gramatica.copiar()
        eliminar_producciones_epsilon(gramatica)
        self.assertEqual(gramatica, copia_antes)
        self.assertEqual(gramatica_a_texto(gramatica), gramatica_a_texto(copia_antes))


if __name__ == "__main__":
    unittest.main()
