"""Pruebas de la Forma Normal de Chomsky: validación y conversión."""

import unittest
from pathlib import Path

from algoritmos.eliminar_epsilon import eliminar_producciones_epsilon
from algoritmos.eliminar_inutiles import eliminar_simbolos_inutiles
from algoritmos.eliminar_unitarias import eliminar_producciones_unitarias
from algoritmos.forma_normal_chomsky import (
    LETRAS_PARA_VARIABLES_NUEVAS,
    es_forma_normal_chomsky,
    generar_nombre_variable_nueva,
    generar_nombre_variable_para_terminal,
    obtener_producciones_fuera_de_cnf,
    reemplazar_terminales_en_cuerpos_largos,
)
from entrada_salida.escritor_gramatica import gramatica_a_texto
from entrada_salida.lector_gramatica import leer_gramatica_desde_archivo, leer_gramatica_desde_texto
from modelos.gramatica import Gramatica

RUTA_GRAMATICAS = Path(__file__).resolve().parent.parent / "gramaticas"


def leer_gramatica_de_ejemplo(nombre_archivo: str) -> Gramatica:
    """Lee una gramática de la carpeta gramaticas/."""
    return leer_gramatica_desde_archivo(RUTA_GRAMATICAS / nombre_archivo)


def simplificar_gramatica(gramatica: Gramatica) -> Gramatica:
    """Aplica los pasos 1–3 de la simplificación: ε → unitarias → inútiles."""
    return eliminar_simbolos_inutiles(
        eliminar_producciones_unitarias(eliminar_producciones_epsilon(gramatica))
    )


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


class PruebaNombresDeVariablesNuevas(unittest.TestCase):
    """Reglas para nombrar las variables que crea la conversión a CNF."""

    def test_usa_letras_desde_la_z(self) -> None:
        nombres_usados = {"E", "X", "T", "Y", "F"}
        self.assertEqual(generar_nombre_variable_nueva(nombres_usados), "Z")
        self.assertEqual(generar_nombre_variable_nueva(nombres_usados), "W")
        self.assertIn("W", nombres_usados)

    def test_cuando_se_acaban_las_letras_usa_c1_c2(self) -> None:
        nombres_usados = set(LETRAS_PARA_VARIABLES_NUEVAS)
        self.assertEqual(generar_nombre_variable_nueva(nombres_usados), "C1")
        self.assertEqual(generar_nombre_variable_nueva(nombres_usados), "C2")

    def test_nombres_para_terminales(self) -> None:
        nombres_usados = {"E"}
        self.assertEqual(generar_nombre_variable_para_terminal("(", nombres_usados), "L")
        self.assertEqual(generar_nombre_variable_para_terminal("a", nombres_usados), "A")
        self.assertEqual(generar_nombre_variable_para_terminal("id", nombres_usados), "I")
        # "+" no tiene letra libre si P ya está ocupada: se usa la primera letra libre desde la Z.
        nombres_usados.add("P")
        self.assertEqual(generar_nombre_variable_para_terminal("+", nombres_usados), "Z")


class PruebaReemplazarTerminales(unittest.TestCase):
    """Construcción (a) de CNF."""

    def test_gramatica_uno_como_en_el_pdf(self) -> None:
        gramatica_simplificada = simplificar_gramatica(leer_gramatica_de_ejemplo("1.txt"))
        resultado, variable_por_terminal = reemplazar_terminales_en_cuerpos_largos(
            gramatica_simplificada
        )
        self.assertEqual(
            list(variable_por_terminal.items()), [("(", "L"), (")", "R"), ("+", "P"), ("*", "M")]
        )
        self.assertEqual(
            gramatica_a_texto(resultado),
            "E -> T X | F Y | L E R | id\n"
            "X -> P T X | P T\n"
            "T -> F Y | L E R | id\n"
            "Y -> M F Y | M F\n"
            "F -> L E R | id\n"
            "L -> (\n"
            "R -> )\n"
            "P -> +\n"
            "M -> *",
        )

    def test_ejemplo_del_libro_usa_los_nombres_del_pdf(self) -> None:
        gramatica_simplificada = simplificar_gramatica(
            leer_gramatica_de_ejemplo("hopcroft_unitarias.txt")
        )
        resultado, variable_por_terminal = reemplazar_terminales_en_cuerpos_largos(
            gramatica_simplificada
        )
        self.assertEqual(
            list(variable_por_terminal.items()),
            [("+", "P"), ("*", "M"), ("(", "L"), (")", "R"), ("a", "A"), ("b", "B"),
             ("0", "Z"), ("1", "O")],
        )
        self.assertEqual(
            gramatica_a_texto(resultado).splitlines()[0],
            "E -> E P T | T M F | L E R | a | b | I A | I B | I Z | I O",
        )

    def test_choque_de_nombres_usa_otra_letra(self) -> None:
        gramatica = leer_gramatica_desde_texto("S -> ( S ) | ( )\nL -> l")
        resultado, variable_por_terminal = reemplazar_terminales_en_cuerpos_largos(gramatica)
        self.assertEqual(variable_por_terminal, {"(": "Z", ")": "R"})
        self.assertEqual(resultado.obtener_producciones("S"), [("Z", "S", "R"), ("Z", "R")])
        self.assertEqual(resultado.obtener_producciones("L"), [("l",)])

    def test_no_modifica_la_gramatica_original(self) -> None:
        gramatica = simplificar_gramatica(leer_gramatica_de_ejemplo("1.txt"))
        texto_antes = gramatica_a_texto(gramatica)
        reemplazar_terminales_en_cuerpos_largos(gramatica)
        self.assertEqual(gramatica_a_texto(gramatica), texto_antes)


if __name__ == "__main__":
    unittest.main()
