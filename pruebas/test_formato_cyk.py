"""Comparaciones exactas del formato de la tabla CYK."""

import unittest

from algoritmos.cyk import cyk
from entrada_salida.formato_cyk import tabla_cyk_a_texto
from entrada_salida.lector_gramatica import leer_gramatica_desde_archivo
from pruebas.test_cyk import RUTA_GRAMATICAS

TABLA_INGLES = """Tabla CYK (fila = longitud de la subcadena, columna = posición inicial):
7 │ {S}
6 │ ∅        {VP}
5 │ ∅        ∅        ∅
4 │ {S}      ∅        ∅        ∅
3 │ ∅        {VP}     ∅        ∅        {PP}
2 │ {S}      ∅        {NP}     ∅        ∅        {NP}
1 │ {NP}     {VP, V}  {Det}    {N}      {P}      {Det}    {N}
  │ she      eats     a        cake     with     a        fork"""


class PruebaFormatoCYK(unittest.TestCase):
    """Comprueba espacios, orden, celdas vacías y tokens."""

    def test_tablas_exactas(self) -> None:
        gramatica = leer_gramatica_desde_archivo(RUTA_GRAMATICAS / "ingles.txt")
        for frase, esperado in [
            ("he cooks", "Tabla CYK (fila = longitud de la subcadena, columna = posición inicial):\n"
             "2 │ {S}\n1 │ {NP}     {VP, V}\n  │ he       cooks"),
            ("she eats a cake with a fork", TABLA_INGLES),
            ("", "Tabla CYK: la frase está vacía."),
        ]:
            with self.subTest(frase=frase):
                self.assertEqual(tabla_cyk_a_texto(cyk(gramatica, frase.split()), gramatica.variables),
                                 esperado)
