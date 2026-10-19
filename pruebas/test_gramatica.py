"""Pruebas del modelo de datos Gramatica."""

import unittest

from modelos.gramatica import Gramatica


def construir_gramatica_uno() -> Gramatica:
    """Construye a mano la gramática de 1.txt (sin usar el lector de archivos)."""
    gramatica = Gramatica("E")
    gramatica.agregar_produccion("E", ("T", "X"))
    gramatica.agregar_produccion("X", ("+", "T", "X"))
    gramatica.agregar_produccion("X", ())
    gramatica.agregar_produccion("T", ("F", "Y"))
    gramatica.agregar_produccion("Y", ("*", "F", "Y"))
    gramatica.agregar_produccion("Y", ())
    gramatica.agregar_produccion("F", ("(", "E", ")"))
    gramatica.agregar_produccion("F", ("id",))
    return gramatica


class PruebaGramatica(unittest.TestCase):
    """Verifica la API de la clase Gramatica."""

    def setUp(self) -> None:
        self.gramatica_uno = construir_gramatica_uno()

    def test_variables_en_orden_de_insercion(self) -> None:
        self.assertEqual(self.gramatica_uno.variables, ["E", "X", "T", "Y", "F"])

    def test_terminales_en_orden_de_aparicion(self) -> None:
        self.assertEqual(self.gramatica_uno.terminales, ["+", "*", "(", ")", "id"])

    def test_el_simbolo_inicial_es_la_primera_variable(self) -> None:
        gramatica = Gramatica("S")
        self.assertEqual(gramatica.variables, ["S"])
        self.assertEqual(gramatica.obtener_producciones("S"), [])

    def test_no_duplica_producciones(self) -> None:
        self.gramatica_uno.agregar_produccion("E", ("T", "X"))
        self.assertEqual(self.gramatica_uno.obtener_producciones("E"), [("T", "X")])

    def test_epsilon_se_guarda_como_tupla_vacia(self) -> None:
        self.assertIn((), self.gramatica_uno.obtener_producciones("X"))

    def test_es_variable_y_es_terminal(self) -> None:
        self.assertTrue(self.gramatica_uno.es_variable("E"))
        self.assertFalse(self.gramatica_uno.es_variable("id"))
        self.assertTrue(self.gramatica_uno.es_terminal("id"))
        self.assertTrue(self.gramatica_uno.es_terminal("("))
        self.assertFalse(self.gramatica_uno.es_terminal("E"))
        self.assertFalse(self.gramatica_uno.es_terminal("pizza"))

    def test_contar_producciones(self) -> None:
        self.assertEqual(self.gramatica_uno.contar_producciones(), 8)

    def test_copiar_devuelve_una_copia_independiente(self) -> None:
        copia = self.gramatica_uno.copiar()
        copia.agregar_produccion("E", ("id",))
        copia.agregar_variable("Z")
        self.assertNotIn(("id",), self.gramatica_uno.obtener_producciones("E"))
        self.assertFalse(self.gramatica_uno.es_variable("Z"))
        self.assertEqual(copia.variables[:5], self.gramatica_uno.variables)

    def test_obtener_producciones_devuelve_una_copia(self) -> None:
        cuerpos_de_e = self.gramatica_uno.obtener_producciones("E")
        cuerpos_de_e.append(("id",))
        self.assertEqual(self.gramatica_uno.obtener_producciones("E"), [("T", "X")])

    def test_eliminar_variable_quita_sus_cuerpos_y_los_que_la_usan(self) -> None:
        self.gramatica_uno.eliminar_variable("Y")
        self.assertFalse(self.gramatica_uno.es_variable("Y"))
        self.assertEqual(self.gramatica_uno.obtener_producciones("T"), [])
        self.assertEqual(self.gramatica_uno.variables, ["E", "X", "T", "F"])
        self.assertNotIn("*", self.gramatica_uno.terminales)

    def test_eliminar_el_simbolo_inicial_lanza_error(self) -> None:
        with self.assertRaises(ValueError):
            self.gramatica_uno.eliminar_variable("E")

    def test_igualdad_ignora_el_orden_de_los_cuerpos(self) -> None:
        gramatica_desordenada = Gramatica("E")
        gramatica_desordenada.agregar_produccion("F", ("id",))
        gramatica_desordenada.agregar_produccion("F", ("(", "E", ")"))
        gramatica_desordenada.agregar_produccion("Y", ())
        gramatica_desordenada.agregar_produccion("Y", ("*", "F", "Y"))
        gramatica_desordenada.agregar_produccion("T", ("F", "Y"))
        gramatica_desordenada.agregar_produccion("X", ())
        gramatica_desordenada.agregar_produccion("X", ("+", "T", "X"))
        gramatica_desordenada.agregar_produccion("E", ("T", "X"))
        self.assertEqual(self.gramatica_uno, gramatica_desordenada)

    def test_igualdad_ignora_variables_sin_producciones(self) -> None:
        copia = self.gramatica_uno.copiar()
        copia.agregar_variable("B")
        self.assertEqual(self.gramatica_uno, copia)

    def test_igualdad_distingue_gramaticas_distintas(self) -> None:
        copia_con_cambio = self.gramatica_uno.copiar()
        copia_con_cambio.agregar_produccion("E", ("id",))
        self.assertNotEqual(self.gramatica_uno, copia_con_cambio)
        self.assertNotEqual(self.gramatica_uno, Gramatica("X"))


if __name__ == "__main__":
    unittest.main()
