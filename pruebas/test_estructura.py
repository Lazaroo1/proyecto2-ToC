"""Prueba de humo: la estructura base del proyecto existe y se puede importar."""

import importlib
import unittest

PAQUETES_DEL_PROYECTO = ("algoritmos", "modelos", "entrada_salida", "pruebas")


class PruebaEstructura(unittest.TestCase):
    """Verifica que los paquetes del proyecto estén completos."""

    def test_los_paquetes_se_pueden_importar(self) -> None:
        for nombre_paquete in PAQUETES_DEL_PROYECTO:
            with self.subTest(paquete=nombre_paquete):
                paquete = importlib.import_module(nombre_paquete)
                self.assertTrue(paquete.__doc__, f"{nombre_paquete} debe tener docstring")


if __name__ == "__main__":
    unittest.main()
