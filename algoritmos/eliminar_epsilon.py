"""Paso 1 de la simplificación: símbolos anulables y producciones ε (Hopcroft §7.1.3).

Una variable A es anulable si A ⇒* ε:

- Base: si A -> ε es una producción, A es anulable.
- Inducción: si A -> C1 C2 … Ck y todos los Ci son anulables, A es anulable.

Para eliminar las producciones ε, cada producción A -> X1 … Xk con m símbolos
anulables se reemplaza por sus 2^m versiones (cada anulable presente o
ausente), excepto la que deja el cuerpo vacío.
"""

from __future__ import annotations

from itertools import product

from modelos.gramatica import Cuerpo, Gramatica


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


def eliminar_producciones_epsilon(gramatica: Gramatica) -> Gramatica:
    """Construye una gramática equivalente sin producciones ε.

    La gramática resultante G1 cumple L(G1) = L(G) − {ε}: genera lo mismo que
    la original salvo la cadena vacía. Todas las variables se conservan en el
    mismo orden, aunque alguna quede sin producciones (de eso se encarga el
    paso de símbolos inútiles).

    Parámetros:
        gramatica: gramática original (no se modifica).

    Retorna:
        Una gramática nueva sin producciones A -> ε.
    """
    anulables = calcular_anulables(gramatica)
    gramatica_sin_epsilon = Gramatica(gramatica.simbolo_inicial)
    for variable in gramatica.variables:
        gramatica_sin_epsilon.agregar_variable(variable)
    for variable in gramatica.variables:
        for cuerpo in gramatica.obtener_producciones(variable):
            for version_del_cuerpo in _generar_versiones_sin_anulables(cuerpo, anulables):
                gramatica_sin_epsilon.agregar_produccion(variable, version_del_cuerpo)
    return gramatica_sin_epsilon


def _generar_versiones_sin_anulables(cuerpo: Cuerpo, anulables: set[str]) -> list[Cuerpo]:
    """Genera las 2^m versiones de un cuerpo con cada anulable presente o ausente.

    Se usa itertools.product([True, False], ...) (True = conservar), así que la
    primera versión es siempre el cuerpo completo. Se descartan el cuerpo vacío
    y los repetidos.
    """
    posiciones_anulables = [
        posicion for posicion, simbolo in enumerate(cuerpo) if simbolo in anulables
    ]
    versiones: list[Cuerpo] = []
    for decisiones_de_conservar in product([True, False], repeat=len(posiciones_anulables)):
        posiciones_quitadas = {
            posicion
            for posicion, conservar in zip(posiciones_anulables, decisiones_de_conservar)
            if not conservar
        }
        version = tuple(
            simbolo for posicion, simbolo in enumerate(cuerpo) if posicion not in posiciones_quitadas
        )
        if version and version not in versiones:
            versiones.append(version)
    return versiones
