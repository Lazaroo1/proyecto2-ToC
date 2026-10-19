"""Paso 3 de la simplificación: eliminación de símbolos inútiles (Hopcroft §7.1.1–7.1.2).

Un símbolo X es útil si existe una derivación S ⇒* αXβ ⇒* w con w formada solo
por terminales. Para ser útil, X debe ser:

1. Generador: X ⇒* w (todo terminal se genera a sí mismo).
2. Alcanzable: existe una derivación S ⇒* αXβ.

El orden importa: primero se quitan los no generadores y DESPUÉS los no
alcanzables, porque quitar un no generador puede dejar símbolos inalcanzables
(ej. en S -> A B | a, A -> b: al quitar B se va S -> A B y A queda inalcanzable).
Teorema: la gramática resultante G' no tiene símbolos inútiles y L(G') = L(G).
"""

from __future__ import annotations

from collections import deque

from modelos.gramatica import Gramatica


def calcular_simbolos_generadores(gramatica: Gramatica) -> set[str]:
    """Calcula los símbolos generadores (los que derivan alguna cadena de terminales).

    Base: todo terminal es generador. Inducción: una variable es generadora si
    tiene un cuerpo cuyos símbolos son todos generadores. Se repite hasta un punto fijo.

    Parámetros:
        gramatica: gramática a analizar.

    Retorna:
        Conjunto con los terminales y las variables generadoras.
    """
    generadores: set[str] = set(gramatica.terminales)
    hubo_cambios = True
    while hubo_cambios:
        hubo_cambios = False
        for variable in gramatica.variables:
            if variable in generadores:
                continue
            if any(
                all(simbolo in generadores for simbolo in cuerpo)
                for cuerpo in gramatica.obtener_producciones(variable)
            ):
                generadores.add(variable)
                hubo_cambios = True
    return generadores


def calcular_simbolos_alcanzables(gramatica: Gramatica) -> set[str]:
    """Calcula los símbolos alcanzables desde el símbolo inicial (BFS por los cuerpos).

    Parámetros:
        gramatica: gramática a analizar.

    Retorna:
        Conjunto con las variables y los terminales alcanzables.
    """
    alcanzables: set[str] = {gramatica.simbolo_inicial}
    pendientes = deque([gramatica.simbolo_inicial])
    while pendientes:
        variable_actual = pendientes.popleft()
        for cuerpo in gramatica.obtener_producciones(variable_actual):
            for simbolo in cuerpo:
                if simbolo in alcanzables:
                    continue
                alcanzables.add(simbolo)
                if gramatica.es_variable(simbolo):
                    pendientes.append(simbolo)
    return alcanzables


def eliminar_simbolos_no_generadores(gramatica: Gramatica) -> Gramatica:
    """Quita las variables no generadoras y todo cuerpo que contenga alguna.

    Parámetros:
        gramatica: gramática original (no se modifica).

    Retorna:
        Una gramática nueva solo con variables generadoras (más el símbolo inicial).
    """
    generadores = calcular_simbolos_generadores(gramatica)
    variables_generadoras = {
        variable for variable in gramatica.variables if variable in generadores
    }
    return _conservar_solo_variables(gramatica, variables_generadoras)


def eliminar_simbolos_no_alcanzables(gramatica: Gramatica) -> Gramatica:
    """Quita las variables no alcanzables desde el símbolo inicial, con sus producciones.

    Parámetros:
        gramatica: gramática original (no se modifica).

    Retorna:
        Una gramática nueva solo con variables alcanzables.
    """
    alcanzables = calcular_simbolos_alcanzables(gramatica)
    variables_alcanzables = {
        variable for variable in gramatica.variables if variable in alcanzables
    }
    return _conservar_solo_variables(gramatica, variables_alcanzables)


def eliminar_simbolos_inutiles(gramatica: Gramatica) -> Gramatica:
    """Quita los símbolos inútiles: PRIMERO los no generadores y DESPUÉS los no alcanzables.

    El orden importa: si se invierte, pueden quedar símbolos inútiles (ver el
    docstring del módulo). El símbolo inicial siempre se conserva, aunque el
    lenguaje sea vacío y quede sin producciones.

    Parámetros:
        gramatica: gramática original (no se modifica).

    Retorna:
        Una gramática nueva sin símbolos inútiles que genera el mismo lenguaje.
    """
    return eliminar_simbolos_no_alcanzables(eliminar_simbolos_no_generadores(gramatica))


def _conservar_solo_variables(gramatica: Gramatica, variables_a_conservar: set[str]) -> Gramatica:
    """Copia la gramática dejando solo algunas variables y los cuerpos que no usan las demás.

    El símbolo inicial siempre se conserva como variable; si no está en
    variables_a_conservar, queda sin producciones (lenguaje vacío).
    """
    gramatica_filtrada = Gramatica(gramatica.simbolo_inicial)
    for variable in gramatica.variables:
        if variable in variables_a_conservar:
            gramatica_filtrada.agregar_variable(variable)
    for variable in gramatica.variables:
        if variable not in variables_a_conservar:
            continue
        for cuerpo in gramatica.obtener_producciones(variable):
            usa_solo_simbolos_conservados = all(
                simbolo in variables_a_conservar or not gramatica.es_variable(simbolo)
                for simbolo in cuerpo
            )
            if usa_solo_simbolos_conservados:
                gramatica_filtrada.agregar_produccion(variable, cuerpo)
    return gramatica_filtrada
