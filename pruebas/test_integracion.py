"""Pruebas completas desde archivos hasta reconocimiento, árboles y consola."""

import itertools
import tempfile
import unittest
from pathlib import Path

from algoritmos.cyk import construir_arbol_sintactico, contar_arboles_de_derivacion, cyk
from algoritmos.forma_normal_chomsky import convertir_a_cnf, es_forma_normal_chomsky
from entrada_salida.lector_gramatica import leer_gramatica_desde_archivo
from entrada_salida.tokenizador import tokenizar_frase
from pruebas.test_cyk import (
    EXPRESIONES_NO, EXPRESIONES_SI, FRASES_INGLES_NO, FRASES_INGLES_SI, RUTA_GRAMATICAS,
)
from pruebas.test_main import ejecutar_programa


class PruebaIntegracion(unittest.TestCase):
    """Verifica los contratos entre todos los módulos de la aplicación."""

    def test_conversion_de_todas_las_gramaticas(self) -> None:
        for ruta in sorted(RUTA_GRAMATICAS.glob("*.txt")):
            with self.subTest(archivo=ruta.name):
                conversion = convertir_a_cnf(leer_gramatica_desde_archivo(ruta))
                self.assertTrue(es_forma_normal_chomsky(conversion.gramatica_cnf))
                self.assertEqual(convertir_a_cnf(conversion.gramatica_cnf).gramatica_cnf,
                                 conversion.gramatica_cnf)

    def test_casos_completos(self) -> None:
        for archivo, aceptadas, rechazadas in [
            ("ingles.txt", FRASES_INGLES_SI, FRASES_INGLES_NO),
            ("1.txt", EXPRESIONES_SI, EXPRESIONES_NO),
            ("anbn.txt", ["", "ab", "aabb"], ["aab", "ba"]),
            ("ambigua.txt", ["id+id*id", "id+id+id*id", "id", "(id)"], ["id+"]),
        ]:
            conversion = convertir_a_cnf(leer_gramatica_desde_archivo(RUTA_GRAMATICAS / archivo))
            gramatica = conversion.gramatica_cnf
            for esperado, frases in [(True, aceptadas), (False, rechazadas)]:
                for frase in frases:
                    with self.subTest(archivo=archivo, frase=frase):
                        tokens = tokenizar_frase(frase, gramatica.terminales)
                        resultado = cyk(gramatica, tokens, conversion.genera_cadena_vacia)
                        arbol = construir_arbol_sintactico(resultado, gramatica.simbolo_inicial)
                        cantidad = contar_arboles_de_derivacion(
                            gramatica, tokens, conversion.genera_cadena_vacia)
                        self.assertEqual(resultado.acepta, esperado)
                        if esperado:
                            self.assertIsNotNone(arbol)
                            self.assertEqual(arbol.simbolo, gramatica.simbolo_inicial)
                            self.assertEqual(arbol.obtener_hojas(), tokens or ["ε"])
                            self.assertGreaterEqual(cantidad, 1)
                        else:
                            self.assertIsNone(arbol)
                            self.assertEqual(cantidad, 0)

    def test_equivalencia_con_cnf_del_catedratico(self) -> None:
        convertida = convertir_a_cnf(
            leer_gramatica_desde_archivo(RUTA_GRAMATICAS / "1.txt")).gramatica_cnf
        referencia = leer_gramatica_desde_archivo(RUTA_GRAMATICAS / "1-cnf.txt")
        cantidad = 0
        for longitud in range(5):
            for secuencia in itertools.product(["id", "+", "*", "(", ")"], repeat=longitud):
                with self.subTest(tokens=secuencia):
                    self.assertEqual(cyk(convertida, list(secuencia)).acepta,
                                     cyk(referencia, list(secuencia)).acepta)
                cantidad += 1
        self.assertEqual(cantidad, 781)

    def test_errores_y_vacia_desde_cli(self) -> None:
        ejecucion = ejecutar_programa("-g", "no_existe.txt", "--sin-imagen")
        self.assertEqual(ejecucion.returncode, 1)
        with tempfile.TemporaryDirectory() as carpeta:
            ruta = Path(carpeta) / "mala.txt"
            ruta.write_text("A B c", encoding="utf-8")
            ejecucion = ejecutar_programa("-g", str(ruta), "--sin-imagen")
            self.assertEqual(ejecucion.returncode, 1)
            self.assertIn("Línea 1", ejecucion.stderr)
        ejecucion = ejecutar_programa("-g", "gramaticas/anbn.txt", "-f", "", "--sin-imagen")
        self.assertEqual(ejecucion.returncode, 0, ejecucion.stderr)
        self.assertIn("Resultado: SÍ", ejecucion.stdout)
