"""Contrasta CYK con reconocimiento y generación independientes de la CNF."""

import itertools
import random
import unittest
from collections import Counter, deque

from algoritmos.cyk import cyk
from algoritmos.forma_normal_chomsky import convertir_a_cnf
from entrada_salida.lector_gramatica import leer_gramatica_desde_archivo
from modelos.gramatica import Gramatica
from pruebas.test_cyk import RUTA_GRAMATICAS


def reconocer_expresion(tokens: tuple[str, ...]) -> bool:
    """Reconocedor descendente de E, T y F; las colas X e Y usan ciclos."""
    posicion = 0

    def consumir(simbolo: str) -> bool:
        nonlocal posicion
        if posicion < len(tokens) and tokens[posicion] == simbolo:
            posicion += 1
            return True
        return False

    def reconocer_factor() -> bool:
        if consumir("id"):
            return True
        if consumir("("):
            return reconocer_suma() and consumir(")")
        return False

    def reconocer_producto() -> bool:
        if not reconocer_factor():
            return False
        while consumir("*"):
            if not reconocer_factor():
                return False
        return True

    def reconocer_suma() -> bool:
        if not reconocer_producto():
            return False
        while consumir("+"):
            if not reconocer_producto():
                return False
        return True

    return reconocer_suma() and posicion == len(tokens)


def generar_frases_cortas(gramatica: Gramatica, limite: int) -> set[tuple[str, ...]]:
    """Enumera por BFS derivaciones izquierdas; requiere una gramática sin ε."""
    inicial = (gramatica.simbolo_inicial,)
    pendientes = deque([inicial])
    visitadas = {inicial}
    frases: set[tuple[str, ...]] = set()
    while pendientes:
        forma = pendientes.popleft()
        posicion = next((posicion for posicion, simbolo in enumerate(forma)
                         if gramatica.es_variable(simbolo)), None)
        if posicion is None:
            frases.add(forma)
            continue
        for cuerpo in gramatica.obtener_producciones(forma[posicion]):
            siguiente = forma[:posicion] + cuerpo + forma[posicion + 1:]
            if len(siguiente) <= limite and siguiente not in visitadas:
                visitadas.add(siguiente)
                pendientes.append(siguiente)
    return frases


def generar_derivacion(gramatica: Gramatica, generador: random.Random) -> list[str]:
    """Deriva desde la CFG original, acortando los cuerpos a partir de profundidad 4."""
    def expandir(simbolo: str, profundidad: int) -> list[str]:
        if not gramatica.es_variable(simbolo):
            return [simbolo]
        cuerpos = gramatica.obtener_producciones(simbolo)
        if profundidad >= 4:
            # Entre cuerpos igualmente cortos, preferir terminales evita ciclos unitarios.
            cuerpo = min(cuerpos, key=lambda cuerpo: (
                len(cuerpo), sum(gramatica.es_variable(parte) for parte in cuerpo)))
        else:
            cuerpo = generador.choice(cuerpos)
        return [token for parte in cuerpo for token in expandir(parte, profundidad + 1)]

    return expandir(gramatica.simbolo_inicial, 0)


class PruebaPropiedadesCYK(unittest.TestCase):
    """Comparaciones exhaustivas y derivaciones con semillas reproducibles."""

    def test_reconocedor_independiente_4206_casos(self) -> None:
        conversion = convertir_a_cnf(leer_gramatica_desde_archivo(RUTA_GRAMATICAS / "1.txt"))
        vocabulario = ["id", "+", "*", "(", ")"]
        generador = random.Random(2024)
        exhaustivas = itertools.chain.from_iterable(
            itertools.product(vocabulario, repeat=longitud) for longitud in range(6))
        aleatorias = [tuple(generador.choice(vocabulario)
                            for posicion in range(generador.randint(6, 12)))
                      for caso in range(300)]
        cantidad = 0
        for tokens in itertools.chain(exhaustivas, aleatorias):
            self.assertEqual(cyk(conversion.gramatica_cnf, list(tokens),
                                 conversion.genera_cadena_vacia).acepta,
                             reconocer_expresion(tokens), tokens)
            cantidad += 1
        self.assertEqual(cantidad, 4206)

    def test_generacion_exhaustiva_ingles_9723_casos(self) -> None:
        gramatica = leer_gramatica_desde_archivo(RUTA_GRAMATICAS / "ingles.txt")
        frases = generar_frases_cortas(gramatica, 4)
        self.assertEqual(Counter(map(len, frases)), {2: 8, 3: 104, 4: 384})
        for frase in sorted(frases):
            self.assertTrue(cyk(gramatica, list(frase)).acepta, frase)
        cantidad = aceptadas = 0
        self.assertEqual(len(gramatica.terminales), 21)
        for longitud in range(1, 4):
            for tokens in itertools.product(gramatica.terminales, repeat=longitud):
                acepta = cyk(gramatica, list(tokens)).acepta
                self.assertEqual(acepta, tokens in frases, tokens)
                aceptadas += acepta
                cantidad += 1
        self.assertEqual((cantidad, aceptadas), (9723, 112))

    def test_derivaciones_de_gramaticas_originales(self) -> None:
        generador = random.Random(7)
        for archivo in ["hopcroft_unitarias.txt", "expresiones_recursiva.txt",
                        "anbn.txt", "ambigua.txt"]:
            original = leer_gramatica_desde_archivo(RUTA_GRAMATICAS / archivo)
            conversion = convertir_a_cnf(original)
            for numero in range(50):
                tokens = generar_derivacion(original, generador)
                with self.subTest(archivo=archivo, caso=numero, tokens=tokens):
                    self.assertTrue(cyk(conversion.gramatica_cnf, tokens,
                                        conversion.genera_cadena_vacia).acepta)
