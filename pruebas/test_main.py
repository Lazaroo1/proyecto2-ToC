"""Pruebas del programa principal (main.py) ejecutándolo como lo haría el usuario."""

import contextlib
import io
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import main
from entrada_salida.lector_gramatica import leer_gramatica_desde_archivo

RAIZ_DEL_PROYECTO = Path(__file__).resolve().parent.parent
RUTA_GRAMATICAS = RAIZ_DEL_PROYECTO / "gramaticas"


def ejecutar_programa(
    *argumentos: str, texto_de_entrada: str | None = None
) -> subprocess.CompletedProcess:
    """Ejecuta main.py en un proceso aparte y captura su salida en UTF-8."""
    entorno = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    return subprocess.run(
        [sys.executable, "main.py", *argumentos],
        cwd=RAIZ_DEL_PROYECTO,
        capture_output=True,
        text=True,
        encoding="utf-8",
        input=texto_de_entrada if texto_de_entrada is not None else "",
        env=entorno,
        timeout=120,
        check=False,
    )


class PruebaConversionDesdeLaConsola(unittest.TestCase):
    """Ejecución de main.py con distintas opciones."""

    def test_paso_a_paso_de_la_gramatica_uno(self) -> None:
        ejecucion = ejecutar_programa("-g", "gramaticas/1.txt")
        self.assertEqual(ejecucion.returncode, 0, ejecucion.stderr)
        self.assertIn("── Paso 5: CNF (b): binarizar cuerpos largos ──", ejecucion.stdout)
        self.assertIn("M -> *", ejecucion.stdout)
        self.assertIn("Tiempo de conversión a CNF:", ejecucion.stdout)

    def test_sin_pasos_usa_la_gramatica_del_ingles_por_defecto(self) -> None:
        ejecucion = ejecutar_programa("--sin-pasos")
        self.assertEqual(ejecucion.returncode, 0, ejecucion.stderr)
        self.assertIn("Det -> a | the", ejecucion.stdout)
        self.assertIn("══ GRAMÁTICA EN CNF ══", ejecucion.stdout)
        self.assertNotIn("── Paso 1", ejecucion.stdout)

    def test_archivo_inexistente(self) -> None:
        ejecucion = ejecutar_programa("-g", "gramaticas/no_existe.txt")
        self.assertEqual(ejecucion.returncode, 1)
        self.assertIn("No se encontró", ejecucion.stderr)

    def test_archivo_mal_formado(self) -> None:
        with tempfile.TemporaryDirectory() as carpeta_temporal:
            ruta_archivo = Path(carpeta_temporal) / "mala.txt"
            ruta_archivo.write_text("A B c\n", encoding="utf-8")
            ejecucion = ejecutar_programa("-g", str(ruta_archivo))
        self.assertEqual(ejecucion.returncode, 1)
        self.assertIn("Línea 1", ejecucion.stderr)

    def test_guardar_cnf(self) -> None:
        with tempfile.TemporaryDirectory() as carpeta_temporal:
            ruta_destino = Path(carpeta_temporal) / "1-cnf-generada.txt"
            ejecucion = ejecutar_programa(
                "-g", "gramaticas/1.txt", "--sin-pasos", "--guardar-cnf", str(ruta_destino)
            )
            self.assertEqual(ejecucion.returncode, 0, ejecucion.stderr)
            gramatica_guardada = leer_gramatica_desde_archivo(ruta_destino)
        gramatica_del_catedratico = leer_gramatica_desde_archivo(RUTA_GRAMATICAS / "1-cnf.txt")
        self.assertEqual(gramatica_guardada, gramatica_del_catedratico)

    def test_main_se_puede_llamar_directamente(self) -> None:
        salida_capturada = io.StringIO()
        with contextlib.redirect_stdout(salida_capturada), patch("builtins.input", side_effect=EOFError):
            codigo_de_salida = main.main(["-g", str(RUTA_GRAMATICAS / "anbn.txt"), "--sin-pasos"])
        self.assertEqual(codigo_de_salida, 0)
        self.assertIn("S -> A Z | A B", salida_capturada.getvalue())

    def test_frases_desde_la_consola(self) -> None:
        for argumentos, textos in [
            (["-f", "She eats a cake with a fork"], ["Resultado: SÍ", "└── fork"]),
            (["-f", "she eats pizza"], ["Resultado: NO", "Aviso:", "pizza"]),
            (["-g", "gramaticas/1.txt", "-f", "(id*id)+id"], ["Resultado: SÍ"]),
            (["-g", "gramaticas/anbn.txt", "-f", ""], ["Resultado: SÍ", "└── ε"]),
        ]:
            with self.subTest(argumentos=argumentos):
                ejecucion = ejecutar_programa(*argumentos, "--sin-imagen")
                self.assertEqual(ejecucion.returncode, 0, ejecucion.stderr)
                for texto in textos:
                    self.assertIn(texto, ejecucion.stdout)

    def test_modo_interactivo(self) -> None:
        ejecucion = ejecutar_programa("--sin-imagen", texto_de_entrada="he cooks\nsalir\n")
        self.assertEqual(ejecucion.returncode, 0, ejecucion.stderr)
        self.assertIn("Resultado: SÍ", ejecucion.stdout)
        self.assertEqual(ejecucion.stdout.count("GRAMÁTICA ORIGINAL"), 1)

    def test_tiempo_y_repeticiones(self) -> None:
        ejecucion = ejecutar_programa("-f", "She eats a cake with a fork", "--sin-imagen")
        self.assertRegex(ejecucion.stdout, r"Tiempo de validación \(CYK\): \d+\.\d{4} ms")
        ejecucion = ejecutar_programa("-f", "he cooks", "--repeticiones", "50", "--sin-imagen")
        self.assertEqual(ejecucion.returncode, 0, ejecucion.stderr)
        self.assertIn("promedio de 50 ejecuciones", ejecucion.stdout)
        ejecucion = ejecutar_programa("--repeticiones", "0")
        self.assertEqual(ejecucion.returncode, 2)
        self.assertIn("mayor o igual a 1", ejecucion.stderr)

    def test_ambiguedad(self) -> None:
        ejecucion = ejecutar_programa("-g", "gramaticas/ambigua.txt", "-f", "id+id*id", "--sin-imagen")
        self.assertEqual(ejecucion.returncode, 0, ejecucion.stderr)
        self.assertIn("Árboles de derivación: 2", ejecucion.stdout)
        self.assertIn("la frase es ambigua", ejecucion.stdout)

    def test_interrupcion_y_opciones(self) -> None:
        with contextlib.redirect_stdout(io.StringIO()), patch("builtins.input", side_effect=KeyboardInterrupt):
            self.assertEqual(main.main(["--sin-imagen"]), 0)
        ejecucion = ejecutar_programa("-f", "he cooks", "--sin-tabla", "--sin-imagen")
        self.assertNotIn("Tabla CYK", ejecucion.stdout)


if __name__ == "__main__":
    unittest.main()
