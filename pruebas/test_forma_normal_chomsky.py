"""Pruebas de la Forma Normal de Chomsky: validación y conversión."""

import unittest
from pathlib import Path

from algoritmos.eliminar_epsilon import eliminar_producciones_epsilon
from algoritmos.eliminar_inutiles import eliminar_simbolos_inutiles
from algoritmos.eliminar_unitarias import eliminar_producciones_unitarias
from algoritmos.forma_normal_chomsky import (
    LETRAS_PARA_VARIABLES_NUEVAS,
    binarizar_cuerpos_largos,
    convertir_a_cnf,
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


class PruebaBinarizarCuerposLargos(unittest.TestCase):
    """Construcción (b) de CNF."""

    def setUp(self) -> None:
        gramatica_simplificada = simplificar_gramatica(leer_gramatica_de_ejemplo("1.txt"))
        self.gramatica_paso_a, _ = reemplazar_terminales_en_cuerpos_largos(gramatica_simplificada)

    def test_gramatica_uno_reutiliza_sufijos(self) -> None:
        resultado, variable_por_sufijo = binarizar_cuerpos_largos(self.gramatica_paso_a)
        self.assertEqual(
            list(variable_por_sufijo.items()),
            [(("E", "R"), "Z"), (("T", "X"), "W"), (("F", "Y"), "V")],
        )
        # Todavía sin reordenar: las variables de terminales van antes que las nuevas.
        self.assertEqual(
            gramatica_a_texto(resultado),
            "E -> T X | F Y | L Z | id\n"
            "X -> P W | P T\n"
            "T -> F Y | L Z | id\n"
            "Y -> M V | M F\n"
            "F -> L Z | id\n"
            "L -> (\n"
            "R -> )\n"
            "P -> +\n"
            "M -> *\n"
            "Z -> E R\n"
            "W -> T X\n"
            "V -> F Y",
        )

    def test_la_misma_variable_sirve_a_varias_cabezas(self) -> None:
        resultado, _ = binarizar_cuerpos_largos(self.gramatica_paso_a)
        for variable in ("E", "T", "F"):
            with self.subTest(variable=variable):
                self.assertIn(("L", "Z"), resultado.obtener_producciones(variable))

    def test_cuerpo_de_longitud_cuatro(self) -> None:
        gramatica = leer_gramatica_desde_texto("A -> B C D E\nB -> b\nC -> c\nD -> d\nE -> e2")
        resultado, variable_por_sufijo = binarizar_cuerpos_largos(gramatica)
        self.assertEqual(
            list(variable_por_sufijo.items()), [(("C", "D", "E"), "Z"), (("D", "E"), "Y")]
        )
        self.assertEqual(resultado.obtener_producciones("A"), [("B", "Z")])
        self.assertEqual(resultado.obtener_producciones("Z"), [("C", "Y")])
        self.assertEqual(resultado.obtener_producciones("Y"), [("D", "E")])

    def test_el_resultado_queda_en_cnf(self) -> None:
        resultado, _ = binarizar_cuerpos_largos(self.gramatica_paso_a)
        self.assertTrue(es_forma_normal_chomsky(resultado))

    def test_cuerpos_cortos_no_cambian(self) -> None:
        gramatica_ingles = leer_gramatica_de_ejemplo("ingles.txt")
        resultado, variable_por_sufijo = binarizar_cuerpos_largos(gramatica_ingles)
        self.assertEqual(variable_por_sufijo, {})
        self.assertEqual(gramatica_a_texto(resultado), gramatica_a_texto(gramatica_ingles))


CNF_FINAL_DEL_LIBRO ="""E -> E C1 | T C2 | L C3 | a | b | I A | I B | I Z | I O
T -> T C2 | L C3 | a | b | I A | I B | I Z | I O
F -> L C3 | a | b | I A | I B | I Z | I O
I -> a | b | I A | I B | I Z | I O
A -> a
B -> b
Z -> 0
O -> 1
P -> +
M -> *
L -> (
R -> )
C1 -> P T
C2 -> M F
C3 -> E R"""
"""Gramática final en CNF del ejemplo del libro, tal como aparece en el PDF (página 3)."""


def renombrar_variables(gramatica: Gramatica, nombres_nuevos: dict[str, str]) -> Gramatica:
    """Devuelve una copia de la gramática con algunas variables renombradas."""
    simbolo_inicial = nombres_nuevos.get(gramatica.simbolo_inicial, gramatica.simbolo_inicial)
    gramatica_renombrada = Gramatica(simbolo_inicial)
    for variable in gramatica.variables:
        for cuerpo in gramatica.obtener_producciones(variable):
            gramatica_renombrada.agregar_produccion(
                nombres_nuevos.get(variable, variable),
                tuple(nombres_nuevos.get(simbolo, simbolo) for simbolo in cuerpo),
            )
    return gramatica_renombrada


class PruebaConvertirACnf(unittest.TestCase):
    """Conversión completa a CNF (los 5 pasos juntos)."""

    def test_gramatica_uno_da_exactamente_1_cnf(self) -> None:
        resultado = convertir_a_cnf(leer_gramatica_de_ejemplo("1.txt"))
        texto_del_catedratico = (RUTA_GRAMATICAS / "1-cnf.txt").read_text(encoding="utf-8-sig")
        self.assertEqual(
            gramatica_a_texto(resultado.gramatica_cnf), texto_del_catedratico.rstrip("\n")
        )
        self.assertEqual(resultado.gramatica_cnf, leer_gramatica_de_ejemplo("1-cnf.txt"))
        self.assertFalse(resultado.genera_cadena_vacia)
        self.assertFalse(resultado.ya_estaba_en_cnf)

    def test_gramatica_uno_guarda_los_cinco_pasos(self) -> None:
        resultado = convertir_a_cnf(leer_gramatica_de_ejemplo("1.txt"))
        self.assertEqual(
            [paso.titulo for paso in resultado.pasos],
            [
                "Eliminar producciones ε",
                "Eliminar producciones unitarias",
                "Eliminar símbolos inútiles",
                "CNF (a): reemplazar terminales en cuerpos largos",
                "CNF (b): binarizar cuerpos largos",
            ],
        )
        self.assertEqual(resultado.pasos[0].detalles["anulables"], {"X", "Y"})
        self.assertEqual(
            resultado.pasos[1].detalles["parejas_unitarias"],
            [("E", "E"), ("E", "T"), ("E", "F"), ("X", "X"), ("T", "T"), ("T", "F"),
             ("Y", "Y"), ("F", "F")],
        )
        self.assertEqual(resultado.pasos[2].detalles["no_generadores"], set())
        self.assertEqual(resultado.pasos[2].detalles["no_alcanzables"], set())
        self.assertEqual(
            resultado.pasos[3].detalles["variables_por_terminal"],
            {"(": "L", ")": "R", "+": "P", "*": "M"},
        )
        self.assertEqual(
            resultado.pasos[4].detalles["variables_por_cuerpo"],
            {("E", "R"): "Z", ("T", "X"): "W", ("F", "Y"): "V"},
        )
        self.assertIs(resultado.pasos[4].gramatica, resultado.gramatica_cnf)

    def test_ejemplo_del_libro_es_la_cnf_del_pdf(self) -> None:
        resultado = convertir_a_cnf(leer_gramatica_de_ejemplo("hopcroft_unitarias.txt"))
        self.assertEqual(
            gramatica_a_texto(resultado.gramatica_cnf),
            "E -> E Y | T X | L W | a | b | I A | I B | I Z | I O\n"
            "T -> T X | L W | a | b | I A | I B | I Z | I O\n"
            "F -> L W | a | b | I A | I B | I Z | I O\n"
            "I -> a | b | I A | I B | I Z | I O\n"
            "Y -> P T\n"
            "X -> M F\n"
            "W -> E R\n"
            "P -> +\n"
            "M -> *\n"
            "L -> (\n"
            "R -> )\n"
            "A -> a\n"
            "B -> b\n"
            "Z -> 0\n"
            "O -> 1",
        )
        # Es la misma gramática del PDF; solo cambian los nombres C1 = Y, C2 = X, C3 = W.
        renombrada = renombrar_variables(resultado.gramatica_cnf, {"Y": "C1", "X": "C2", "W": "C3"})
        self.assertEqual(renombrada, leer_gramatica_desde_texto(CNF_FINAL_DEL_LIBRO))

    def test_recursion_por_la_izquierda(self) -> None:
        resultado = convertir_a_cnf(leer_gramatica_de_ejemplo("expresiones_recursiva.txt"))
        self.assertEqual(
            gramatica_a_texto(resultado.gramatica_cnf),
            "E -> E Z | T Y | L X | id\n"
            "T -> T Y | L X | id\n"
            "F -> L X | id\n"
            "Z -> P T\n"
            "Y -> M F\n"
            "X -> E R\n"
            "P -> +\n"
            "M -> *\n"
            "L -> (\n"
            "R -> )",
        )

    def test_gramatica_del_ingles_ya_estaba_en_cnf(self) -> None:
        gramatica_ingles = leer_gramatica_de_ejemplo("ingles.txt")
        resultado = convertir_a_cnf(gramatica_ingles)
        self.assertTrue(resultado.ya_estaba_en_cnf)
        self.assertEqual(resultado.gramatica_cnf, gramatica_ingles)
        self.assertEqual(
            gramatica_a_texto(resultado.gramatica_cnf), gramatica_a_texto(gramatica_ingles)
        )

    def test_anbn_genera_la_cadena_vacia(self) -> None:
        resultado = convertir_a_cnf(leer_gramatica_de_ejemplo("anbn.txt"))
        self.assertTrue(resultado.genera_cadena_vacia)
        self.assertEqual(
            gramatica_a_texto(resultado.gramatica_cnf), "S -> A Z | A B\nZ -> S B\nA -> a\nB -> b"
        )

    def test_ejemplo_de_simbolos_inutiles(self) -> None:
        resultado = convertir_a_cnf(leer_gramatica_de_ejemplo("inutiles.txt"))
        self.assertEqual(gramatica_a_texto(resultado.gramatica_cnf), "S -> a")
        self.assertEqual(resultado.pasos[2].detalles["no_generadores"], {"B"})
        self.assertEqual(resultado.pasos[2].detalles["no_alcanzables"], {"A", "b"})

    def test_lenguaje_vacio_no_falla(self) -> None:
        resultado = convertir_a_cnf(leer_gramatica_desde_texto("S -> A B\nA -> a A\nB -> b"))
        self.assertEqual(resultado.gramatica_cnf.contar_producciones(), 0)
        self.assertEqual(resultado.gramatica_cnf.simbolo_inicial, "S")

    def test_todas_las_gramaticas_quedan_en_cnf_sin_tocar_la_original(self) -> None:
        for ruta_archivo in sorted(RUTA_GRAMATICAS.glob("*.txt")):
            with self.subTest(archivo=ruta_archivo.name):
                gramatica = leer_gramatica_desde_archivo(ruta_archivo)
                texto_antes = gramatica_a_texto(gramatica)
                resultado = convertir_a_cnf(gramatica)
                self.assertTrue(es_forma_normal_chomsky(resultado.gramatica_cnf))
                self.assertEqual(gramatica_a_texto(gramatica), texto_antes)
                self.assertEqual(resultado.gramatica_cnf.variables[0], gramatica.simbolo_inicial)


if __name__ == "__main__":
    unittest.main()
