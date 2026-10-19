"""Casos de referencia del enunciado y límites del reconocedor CYK."""

import unittest
from pathlib import Path

from algoritmos.cyk import contar_arboles_de_derivacion, cyk
from algoritmos.forma_normal_chomsky import convertir_a_cnf
from entrada_salida.lector_gramatica import leer_gramatica_desde_archivo
from entrada_salida.tokenizador import tokenizar_frase
from entrada_salida.escritor_gramatica import gramatica_a_texto

RUTA_GRAMATICAS = Path(__file__).resolve().parent.parent / "gramaticas"
FRASES_INGLES_SI = [
    "She eats a cake with a fork", "The cat drinks the beer.", "he cooks", "the dog eats",
    "she cuts the meat with a knife", "he drinks the juice in the oven",
    "the cat cooks a soup with a spoon in the oven", "a dog drinks the soup",
    "the fork eats the cat", "a cake eats she",
]
FRASES_INGLES_NO = [
    "She eats a cake with", "cat drinks the beer", "the cat drinks beer", "the cat the beer",
    "he she eats", "eats a cake", "she with a fork eats", "the the cat eats", "she eats pizza",
    "she eats athe cake", "",
]
EXPRESIONES_SI = ["(id*id)+id", "( id * id ) + id", "id", "id+id", "id*id", "((id))",
                  "id+id*id", "(id+id)*id"]
EXPRESIONES_NO = ["(id*id", "id+", "+id", "id id", "()", "id**id", "", "idid"]


class PruebaCYK(unittest.TestCase):
    """Verifica aceptación, tabla, CNF y ausencia de mutaciones."""

    def test_casos_del_enunciado(self) -> None:
        for archivo, aceptadas, rechazadas in [
            ("ingles.txt", FRASES_INGLES_SI, FRASES_INGLES_NO),
            ("1.txt", EXPRESIONES_SI, EXPRESIONES_NO),
            ("1-cnf.txt", EXPRESIONES_SI, EXPRESIONES_NO),
            ("anbn.txt", ["", "ab", "aabb"], ["aab", "ba"]),
        ]:
            conversion = convertir_a_cnf(leer_gramatica_desde_archivo(RUTA_GRAMATICAS / archivo))
            gramatica = conversion.gramatica_cnf
            for esperado, frases in [(True, aceptadas), (False, rechazadas)]:
                for frase in frases:
                    with self.subTest(archivo=archivo, frase=frase):
                        tokens = tokenizar_frase(frase, gramatica.terminales)
                        copia = gramatica.copiar()
                        resultado = cyk(gramatica, tokens, conversion.genera_cadena_vacia)
                        self.assertEqual(resultado.acepta, esperado)
                        self.assertEqual(gramatica, copia)
                        self.assertEqual(resultado.tokens, tokens)
                        self.assertIsNot(resultado.tokens, tokens)

    def test_tabla_he_cooks(self) -> None:
        gramatica = leer_gramatica_desde_archivo(RUTA_GRAMATICAS / "ingles.txt")
        resultado = cyk(gramatica, ["he", "cooks"])
        self.assertEqual(resultado.tabla, [[{"NP"}, {"S"}], [set(), {"VP", "V"}]])

    def test_retroceso_completo_consistente_y_determinista(self) -> None:
        gramatica = leer_gramatica_desde_archivo(RUTA_GRAMATICAS / "ingles.txt")
        tokens = tokenizar_frase(FRASES_INGLES_SI[0], gramatica.terminales)
        resultado = cyk(gramatica, tokens)
        self.assertEqual(resultado.retroceso[(0, 6, "S")], (0, "NP", "VP"))
        self.assertEqual(resultado.retroceso, cyk(gramatica, tokens).retroceso)
        for inicio, fila in enumerate(resultado.tabla):
            for fin, celda in enumerate(fila):
                for cabeza in celda:
                    origen = resultado.retroceso[(inicio, fin, cabeza)]
                    if isinstance(origen, str):
                        self.assertEqual(inicio, fin)
                        self.assertEqual(origen, tokens[inicio])
                        self.assertIn((origen,), gramatica.obtener_producciones(cabeza))
                    else:
                        corte, izquierda, derecha = origen
                        self.assertTrue(inicio <= corte < fin)
                        self.assertIn(izquierda, resultado.tabla[inicio][corte])
                        self.assertIn(derecha, resultado.tabla[corte + 1][fin])
                        self.assertIn((izquierda, derecha), gramatica.obtener_producciones(cabeza))

    def test_vacia_y_gramatica_fuera_de_cnf(self) -> None:
        original = leer_gramatica_desde_archivo(RUTA_GRAMATICAS / "1.txt")
        with self.assertRaises(ValueError):
            cyk(original, [])
        gramatica = convertir_a_cnf(original).gramatica_cnf
        self.assertFalse(cyk(gramatica, []).acepta)
        self.assertTrue(cyk(gramatica, [], True).acepta)
        self.assertEqual(cyk(gramatica, []).tabla, [])

    def test_conteo_ingles_y_vacia(self) -> None:
        gramatica = leer_gramatica_desde_archivo(RUTA_GRAMATICAS / "ingles.txt")
        for esperado, frases in [(1, FRASES_INGLES_SI), (0, FRASES_INGLES_NO)]:
            for frase in frases:
                with self.subTest(frase=frase):
                    tokens = tokenizar_frase(frase, gramatica.terminales)
                    self.assertEqual(contar_arboles_de_derivacion(gramatica, tokens), esperado)
        original = leer_gramatica_desde_archivo(RUTA_GRAMATICAS / "anbn.txt")
        gramatica = convertir_a_cnf(original).gramatica_cnf
        self.assertEqual(contar_arboles_de_derivacion(gramatica, [], True), 1)
        self.assertEqual(contar_arboles_de_derivacion(gramatica, []), 0)
        with self.assertRaises(ValueError):
            contar_arboles_de_derivacion(original, [])

    def test_ambiguedad_y_cnf_exacta(self) -> None:
        gramatica = convertir_a_cnf(
            leer_gramatica_desde_archivo(RUTA_GRAMATICAS / "ambigua.txt")).gramatica_cnf
        self.assertEqual(gramatica_a_texto(gramatica),
                         "E -> E Z | E Y | L X | id\nZ -> P E\nY -> M E\nX -> E R\n"
                         "P -> +\nM -> *\nL -> (\nR -> )")
        for frase, esperado in [("id+id*id", 2), ("id+id+id*id", 5), ("id", 1),
                                 ("(id)", 1), ("id+", 0)]:
            with self.subTest(frase=frase):
                tokens = tokenizar_frase(frase, gramatica.terminales)
                self.assertEqual(contar_arboles_de_derivacion(gramatica, tokens), esperado)
        resultado = cyk(gramatica, tokenizar_frase("id+id*id", gramatica.terminales))
        self.assertEqual(resultado.retroceso[(0, 4, "E")], (0, "E", "Z"))
