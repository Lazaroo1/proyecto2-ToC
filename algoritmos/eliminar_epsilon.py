"""Paso 1 de la simplificación: símbolos anulables y producciones ε (Hopcroft §7.1.3).

Una variable A es anulable si A ⇒* ε:

- Base: si A -> ε es una producción, A es anulable.
- Inducción: si A -> C1 C2 … Ck y todos los Ci son anulables, A es anulable.
"""

from __future__ import annotations

from modelos.gramatica import Gramatica


def calcular_anulables(gramatica: Gramatica) -> set[str]:
    """Calcula las variables anulables, es decir, las que derivan la cadena vacía.

    Se repite la regla de inducción hasta llegar a un punto fijo (ninguna
    variable nueva se vuelve anulable en una pasada completa).

    Parámetros:
        gramatica: gramática de la que se buscan los anulables.

    Retorna:
        Conjunto con toda variable A tal que A ⇒* ε.
    """
    anulables: set[str] = set()
    hubo_cambios = True
    while hubo_cambios:
        hubo_cambios = False
        for variable in gramatica.variables:
            if variable in anulables:
                continue
            # Base: el cuerpo vacío () cumple all() de inmediato.
            # Inducción: todos los símbolos del cuerpo ya son anulables.
            if any(
                all(simbolo in anulables for simbolo in cuerpo)
                for cuerpo in gramatica.obtener_producciones(variable)
            ):
                anulables.add(variable)
                hubo_cambios = True
    return anulables
