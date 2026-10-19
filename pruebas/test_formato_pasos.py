"""Pruebas del texto del paso a paso de la conversión a CNF."""

import unittest
from pathlib import Path

from algoritmos.forma_normal_chomsky import convertir_a_cnf
from entrada_salida.escritor_gramatica import describir_gramatica
from entrada_salida.formato_pasos import formatear_conversion, formatear_gramatica_con_titulo
from entrada_salida.lector_gramatica import leer_gramatica_desde_archivo, leer_gramatica_desde_texto

RUTA_GRAMATICAS = Path(__file__).resolve().parent.parent / "gramaticas"


def obtener_paso_a_paso(nombre_archivo: str) -> str:
    """Convierte una gramática de gramaticas/ y devuelve el texto del paso a paso."""
    gramatica = leer_gramatica_desde_archivo(RUTA_GRAMATICAS / nombre_archivo)
    return formatear_conversion(convertir_a_cnf(gramatica))


class PruebaPasoAPasoGramaticaUno(unittest.TestCase):
    """El paso a paso de 1.txt debe verse como el ejemplo del catedrático."""

    def setUp(self) -> None:
        self.texto = obtener_paso_a_paso("1.txt")
        self.lineas = self.texto.splitlines()

    def test_detalles_de_cada_paso(self) -> None:
        self.assertIn("Anulables: X, Y", self.lineas)
        self.assertIn(
            "Parejas unitarias: (E, E), (E, T), (E, F), (X, X), (T, T), (T, F), (Y, Y), (F, F)",
            self.lineas,
        )
        self.assertIn("No generadores: ninguno", self.lineas)
        self.assertIn("No alcanzables: ninguno", self.lineas)
        self.assertIn("Variables nuevas: L -> (, R -> ), P -> +, M -> *", self.lineas)
        self.assertIn("Variables nuevas: Z -> E R, W -> T X, V -> F Y", self.lineas)

    def test_los_pasos_aparecen_en_orden(self) -> None:
        encabezados = [
            "══ GRAMÁTICA ORIGINAL ══",
            "── Paso 1: Eliminar producciones ε ──",
            "── Paso 2: Eliminar producciones unitarias ──",
            "── Paso 3: Eliminar símbolos inútiles ──",
            "── Paso 4: CNF (a): reemplazar terminales en cuerpos largos ──",
            "── Paso 5: CNF (b): binarizar cuerpos largos ──",
            "══ GRAMÁTICA EN CNF ══",
        ]
        posiciones = [self.lineas.index(encabezado) for encabezado in encabezados]
        self.assertEqual(posiciones, sorted(posiciones))

    def test_el_paso_sin_cambios_lo_indica(self) -> None:
        posicion_paso_3 = self.lineas.index("── Paso 3: Eliminar símbolos inútiles ──")
        self.assertEqual(self.lineas[posicion_paso_3 + 3], "(sin cambios)")

    def test_la_cnf_final_es_1_cnf(self) -> None:
        lineas_1_cnf = (RUTA_GRAMATICAS / "1-cnf.txt").read_text(encoding="utf-8-sig").splitlines()
        posicion_encabezado = self.lineas.index("══ GRAMÁTICA EN CNF ══")
        lineas_despues_del_encabezado = self.lineas[
            posicion_encabezado + 1 : posicion_encabezado + 1 + len(lineas_1_cnf)
        ]
        self.assertEqual(lineas_despues_del_encabezado, lineas_1_cnf)


class PruebaPasoAPasoOtrasGramaticas(unittest.TestCase):
    """Mensajes especiales: sin cambios, cadena vacía y símbolos eliminados."""

    def test_gramatica_del_ingles_ya_estaba_en_cnf(self) -> None:
        texto = obtener_paso_a_paso("ingles.txt")
        self.assertEqual(texto.count("(sin cambios)"), 5)
        self.assertIn("Anulables: ninguno", texto)
        self.assertIn("La gramática ya estaba en CNF: la conversión no cambia nada.", texto)
        self.assertNotIn("ε ∈ L(G)", texto)

    def test_anbn_avisa_la_cadena_vacia(self) -> None:
        texto = obtener_paso_a_paso("anbn.txt")
        self.assertIn("Anulables: S", texto)
        self.assertIn("ε ∈ L(G)", texto)

    def test_simbolos_inutiles_en_el_orden_de_la_gramatica(self) -> None:
        texto = obtener_paso_a_paso("inutiles.txt")
        self.assertIn("No generadores: B", texto)
        self.assertIn("No alcanzables: A, b", texto)

    def test_cuerpo_largo_muestra_el_cuerpo_real_de_cada_variable(self) -> None:
        gramatica = leer_gramatica_desde_texto("A -> B C D E\nB -> b\nC -> c\nD -> d\nE -> e2")
        texto = formatear_conversion(convertir_a_cnf(gramatica))
        self.assertIn("Variables nuevas: Z -> C Y, Y -> D E", texto)

    def test_gramatica_con_titulo(self) -> None:
        gramatica = leer_gramatica_desde_archivo(RUTA_GRAMATICAS / "1.txt")
        lineas = formatear_gramatica_con_titulo("PRUEBA", gramatica).splitlines()
        self.assertEqual(lineas[0], "══ PRUEBA ══")
        self.assertEqual(lineas[1], "E -> T X")
        self.assertEqual(lineas[-1], describir_gramatica(gramatica))


if __name__ == "__main__":
    unittest.main()
