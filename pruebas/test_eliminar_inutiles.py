"""Pruebas del paso 3: generadores, alcanzables y eliminación de símbolos inútiles."""

import unittest
from pathlib import Path

from algoritmos.eliminar_epsilon import eliminar_producciones_epsilon
from algoritmos.eliminar_inutiles import (
    calcular_simbolos_alcanzables,
    calcular_simbolos_generadores,
    eliminar_simbolos_inutiles,
    eliminar_simbolos_no_alcanzables,
    eliminar_simbolos_no_generadores,
)
from algoritmos.eliminar_unitarias import eliminar_producciones_unitarias
from entrada_salida.escritor_gramatica import gramatica_a_texto
from entrada_salida.lector_gramatica import leer_gramatica_desde_archivo, leer_gramatica_desde_texto
from modelos.gramatica import Gramatica

RUTA_GRAMATICAS = Path(__file__).resolve().parent.parent / "gramaticas"


def leer_gramatica_de_ejemplo(nombre_archivo: str) -> Gramatica:
    """Lee una gramática de la carpeta gramaticas/."""
    return leer_gramatica_desde_archivo(RUTA_GRAMATICAS / nombre_archivo)


class PruebaEjemploDelLibro(unittest.TestCase):
    """Ejemplo del PDF: S -> A B | a, A -> b."""

    def setUp(self) -> None:
        self.gramatica = leer_gramatica_de_ejemplo("inutiles.txt")

    def test_generadores(self) -> None:
        self.assertEqual(calcular_simbolos_generadores(self.gramatica), {"S", "A", "a", "b"})

    def test_alcanzables_de_la_gramatica_original(self) -> None:
        self.assertEqual(calcular_simbolos_alcanzables(self.gramatica), {"S", "A", "B", "a", "b"})

    def test_resultado_final(self) -> None:
        resultado = eliminar_simbolos_inutiles(self.gramatica)
        self.assertEqual(gramatica_a_texto(resultado), "S -> a")
        self.assertEqual(resultado.variables, ["S"])
        self.assertEqual(resultado.terminales, ["a"])

    def test_el_orden_importa(self) -> None:
        orden_incorrecto = eliminar_simbolos_no_generadores(
            eliminar_simbolos_no_alcanzables(self.gramatica)
        )
        self.assertTrue(orden_incorrecto.es_variable("A"))
        self.assertEqual(gramatica_a_texto(orden_incorrecto), "S -> a\nA -> b")
        self.assertFalse(eliminar_simbolos_inutiles(self.gramatica).es_variable("A"))


class PruebaCasosBorde(unittest.TestCase):
    """Lenguaje vacío, gramáticas sin inútiles e inmutabilidad."""

    def test_lenguaje_vacio_conserva_el_simbolo_inicial(self) -> None:
        gramatica = leer_gramatica_desde_texto("S -> A B\nA -> a A\nB -> b")
        resultado = eliminar_simbolos_inutiles(gramatica)
        self.assertEqual(resultado.simbolo_inicial, "S")
        self.assertEqual(resultado.variables, ["S"])
        self.assertEqual(resultado.contar_producciones(), 0)

    def test_gramatica_uno_simplificada_no_cambia(self) -> None:
        gramatica_paso_2 = eliminar_producciones_unitarias(
            eliminar_producciones_epsilon(leer_gramatica_de_ejemplo("1.txt"))
        )
        resultado = eliminar_simbolos_inutiles(gramatica_paso_2)
        self.assertEqual(gramatica_a_texto(resultado), gramatica_a_texto(gramatica_paso_2))

    def test_gramatica_del_ingles_queda_igual(self) -> None:
        gramatica_ingles = leer_gramatica_de_ejemplo("ingles.txt")
        resultado = eliminar_simbolos_inutiles(gramatica_ingles)
        self.assertEqual(gramatica_a_texto(resultado), gramatica_a_texto(gramatica_ingles))

    def test_quita_variables_inalcanzables_con_sus_producciones(self) -> None:
        gramatica = leer_gramatica_desde_texto("S -> a\nA -> b A | c")
        resultado = eliminar_simbolos_no_alcanzables(gramatica)
        self.assertEqual(gramatica_a_texto(resultado), "S -> a")

    def test_no_modifica_la_gramatica_original(self) -> None:
        gramatica = leer_gramatica_de_ejemplo("inutiles.txt")
        copia_antes = gramatica.copiar()
        eliminar_simbolos_inutiles(gramatica)
        self.assertEqual(gramatica.variables, copia_antes.variables)
        self.assertEqual(gramatica_a_texto(gramatica), gramatica_a_texto(copia_antes))


if __name__ == "__main__":
    unittest.main()
