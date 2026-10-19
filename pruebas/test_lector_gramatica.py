"""Pruebas del lector de gramáticas (texto/archivo -> Gramatica)."""

import tempfile
import unittest
from pathlib import Path

from entrada_salida.lector_gramatica import (
    ErrorFormatoGramatica,
    leer_gramatica_desde_archivo,
    leer_gramatica_desde_texto,
)

RUTA_GRAMATICAS = Path(__file__).resolve().parent.parent / "gramaticas"


class PruebaLectorConArchivosReales(unittest.TestCase):
    """Lectura de las gramáticas de la carpeta gramaticas/."""

    def test_lee_la_gramatica_uno(self) -> None:
        gramatica = leer_gramatica_desde_archivo(RUTA_GRAMATICAS / "1.txt")
        self.assertEqual(gramatica.simbolo_inicial, "E")
        self.assertEqual(gramatica.variables, ["E", "X", "T", "Y", "F"])
        self.assertEqual(gramatica.terminales, ["+", "*", "(", ")", "id"])
        self.assertEqual(gramatica.obtener_producciones("X"), [("+", "T", "X"), ()])
        self.assertEqual(gramatica.obtener_producciones("F"), [("(", "E", ")"), ("id",)])

    def test_lee_la_gramatica_del_ingles_juntando_lineas_repetidas(self) -> None:
        gramatica = leer_gramatica_desde_archivo(RUTA_GRAMATICAS / "ingles.txt")
        self.assertEqual(gramatica.simbolo_inicial, "S")
        self.assertEqual(gramatica.variables, ["S", "VP", "PP", "NP", "V", "P", "N", "Det"])
        self.assertEqual(len(gramatica.terminales), 21)
        self.assertEqual(
            gramatica.obtener_producciones("VP"),
            [("VP", "PP"), ("V", "NP"), ("cooks",), ("drinks",), ("eats",), ("cuts",)],
        )
        self.assertEqual(len(gramatica.obtener_producciones("N")), 11)

    def test_simbolo_en_mayuscula_sin_producciones_es_variable(self) -> None:
        gramatica = leer_gramatica_desde_archivo(RUTA_GRAMATICAS / "inutiles.txt")
        self.assertTrue(gramatica.es_variable("B"))
        self.assertEqual(gramatica.obtener_producciones("B"), [])
        self.assertEqual(gramatica.variables, ["S", "A", "B"])
        self.assertEqual(gramatica.terminales, ["a", "b"])

    def test_tolera_el_bom_del_bloc_de_notas(self) -> None:
        with tempfile.TemporaryDirectory() as carpeta_temporal:
            ruta_archivo = Path(carpeta_temporal) / "con_bom.txt"
            ruta_archivo.write_text("S -> a\n", encoding="utf-8-sig")
            gramatica = leer_gramatica_desde_archivo(ruta_archivo)
        self.assertEqual(gramatica.simbolo_inicial, "S")

    def test_archivo_inexistente_lanza_file_not_found(self) -> None:
        with self.assertRaises(FileNotFoundError):
            leer_gramatica_desde_archivo(RUTA_GRAMATICAS / "no_existe.txt")


class PruebaLectorDesdeTexto(unittest.TestCase):
    """Variantes del formato aceptadas por el lector."""

    def test_acepta_la_flecha_unicode(self) -> None:
        con_flecha_ascii = leer_gramatica_desde_texto("S -> a S | b")
        con_flecha_unicode = leer_gramatica_desde_texto("S → a S | b")
        self.assertEqual(con_flecha_ascii, con_flecha_unicode)

    def test_epsilon_con_letra_griega_equivale_a_e(self) -> None:
        con_e = leer_gramatica_desde_texto("S -> a S | e")
        con_epsilon = leer_gramatica_desde_texto("S -> a S | ε")
        self.assertEqual(con_e, con_epsilon)
        self.assertIn((), con_epsilon.obtener_producciones("S"))

    def test_ignora_comentarios_y_lineas_vacias(self) -> None:
        texto = "# comentario inicial\n\nS -> A\n   \n# otro comentario\nA -> a\n"
        gramatica = leer_gramatica_desde_texto(texto)
        self.assertEqual(gramatica.variables, ["S", "A"])
        self.assertEqual(gramatica.contar_producciones(), 2)


class PruebaErroresDeFormato(unittest.TestCase):
    """Cada error de formato lanza ErrorFormatoGramatica con la línea correcta."""

    def verificar_error(self, texto: str, numero_linea_esperado: int | None) -> None:
        with self.assertRaises(ErrorFormatoGramatica) as contexto:
            leer_gramatica_desde_texto(texto)
        self.assertEqual(contexto.exception.numero_linea, numero_linea_esperado)
        if numero_linea_esperado is not None:
            self.assertIn(f"Línea {numero_linea_esperado}", str(contexto.exception))

    def test_texto_sin_producciones(self) -> None:
        self.verificar_error("", None)
        self.verificar_error("# solo comentarios\n\n", None)

    def test_linea_sin_flecha(self) -> None:
        self.verificar_error("S -> a\nA b c", 2)

    def test_cabeza_vacia(self) -> None:
        self.verificar_error("S -> a\n\n# comentario\n -> b", 4)

    def test_cabeza_con_espacios(self) -> None:
        self.verificar_error("A B -> c", 1)

    def test_cabeza_que_es_epsilon(self) -> None:
        self.verificar_error("S -> a\ne -> b", 2)

    def test_alternativa_vacia(self) -> None:
        self.verificar_error("S -> a\nA -> a | | b", 2)
        self.verificar_error("A -> ", 1)

    def test_epsilon_mezclado_con_otros_simbolos(self) -> None:
        self.verificar_error("S -> a e b", 1)

    def test_mas_de_una_flecha(self) -> None:
        self.verificar_error("S -> a -> b", 1)


if __name__ == "__main__":
    unittest.main()
