"""Estructuras exactas y hojas de los árboles recuperados de CYK."""

import unittest

from algoritmos.cyk import construir_arbol_sintactico, cyk
from algoritmos.forma_normal_chomsky import convertir_a_cnf
from entrada_salida.lector_gramatica import leer_gramatica_desde_archivo
from entrada_salida.tokenizador import tokenizar_frase
from entrada_salida.visualizacion_arbol import arbol_a_corchetes
from modelos.nodo_arbol import NodoArbol
from pruebas.test_cyk import EXPRESIONES_SI, FRASES_INGLES_SI, RUTA_GRAMATICAS

ARBOL_INGLES = (
    "[S [NP she] [VP [VP [V eats] [NP [Det a] [N cake]]] "
    "[PP [P with] [NP [Det a] [N fork]]]]]"
)
ARBOL_EXPRESION = "[E [T [L (] [Z [E [F id] [Y [M *] [F id]]] [R )]]] [X [P +] [T id]]]"


class PruebaArbolSintactico(unittest.TestCase):
    """Verifica estructuras y casos especiales del árbol."""

    def test_arboles_aceptados(self) -> None:
        for archivo, frases, esperado in [("ingles.txt", FRASES_INGLES_SI, ARBOL_INGLES),
                                          ("1.txt", EXPRESIONES_SI, ARBOL_EXPRESION)]:
            gramatica = convertir_a_cnf(
                leer_gramatica_desde_archivo(RUTA_GRAMATICAS / archivo)).gramatica_cnf
            for posicion, frase in enumerate(frases):
                with self.subTest(frase=frase):
                    tokens = tokenizar_frase(frase, gramatica.terminales)
                    arbol = construir_arbol_sintactico(cyk(gramatica, tokens), gramatica.simbolo_inicial)
                    self.assertIsNotNone(arbol)
                    self.assertEqual(arbol.simbolo, gramatica.simbolo_inicial)
                    self.assertEqual(arbol.obtener_hojas(), tokens)
                    if posicion == 0:
                        self.assertEqual(arbol_a_corchetes(arbol), esperado)

    def test_rechazo_vacia_altura_y_nodos(self) -> None:
        gramatica = leer_gramatica_desde_archivo(RUTA_GRAMATICAS / "ingles.txt")
        self.assertIsNone(construir_arbol_sintactico(cyk(gramatica, ["pizza"]), "S"))
        arbol = construir_arbol_sintactico(cyk(gramatica, ["he", "cooks"]), "S")
        self.assertEqual(arbol.contar_nodos(), 5)
        self.assertEqual(arbol.calcular_altura(), 2)
        self.assertEqual(NodoArbol("he").calcular_altura(), 0)
        gramatica = convertir_a_cnf(
            leer_gramatica_desde_archivo(RUTA_GRAMATICAS / "anbn.txt")).gramatica_cnf
        self.assertEqual(construir_arbol_sintactico(cyk(gramatica, [], True), "S"),
                         NodoArbol("S", [NodoArbol("ε")]))
