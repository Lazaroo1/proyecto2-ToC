"""Pruebas del programa principal (main.py) ejecutándolo como lo haría el usuario."""

import contextlib
import io
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

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
        input=texto_de_entrada,
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
        with contextlib.redirect_stdout(salida_capturada):
            codigo_de_salida = main.main(["-g", str(RUTA_GRAMATICAS / "anbn.txt"), "--sin-pasos"])
        self.assertEqual(codigo_de_salida, 0)
        self.assertIn("S -> A Z | A B", salida_capturada.getvalue())


if __name__ == "__main__":
    unittest.main()
