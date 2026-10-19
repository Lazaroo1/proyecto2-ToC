"""Paso 2 de la simplificación: eliminación de producciones unitarias (Hopcroft §7.1.4).

Una producción A -> B es unitaria si B es una variable. (A, B) es una pareja
unitaria si A ⇒* B usando solo producciones unitarias:

- Base: (A, A) es pareja unitaria para toda variable A.
- Inducción: si (A, B) es pareja unitaria y B -> C es unitaria, (A, C) también.

Construcción: para cada pareja (A, B) se agregan a A todas las producciones
NO unitarias de B. Como (A, A) siempre es pareja, A conserva sus propias
producciones no unitarias.
"""

from __future__ import annotations

from collections import deque

from modelos.gramatica import Cuerpo, Gramatica


def es_produccion_unitaria(gramatica: Gramatica, cuerpo: Cuerpo) -> bool:
    """Indica si el cuerpo es una sola variable (producción A -> B).

    Parámetros:
        gramatica: gramática a la que pertenece el cuerpo.
        cuerpo: cuerpo de la producción.

    Retorna:
        True si el cuerpo tiene exactamente un símbolo y ese símbolo es variable.
    """
    return len(cuerpo) == 1 and gramatica.es_variable(cuerpo[0])


def calcular_parejas_unitarias(gramatica: Gramatica) -> list[tuple[str, str]]:
    """Calcula todas las parejas unitarias (A, B) tales que A ⇒* B.

    Para cada variable A (en orden) se hace un BFS que solo sigue producciones
    unitarias: primero va (A, A) y luego cada (A, B) en el orden en que se
    descubre. Los ciclos (A -> B, B -> A) no causan recursión infinita.

    Parámetros:
        gramatica: gramática a analizar.

    Retorna:
        Lista de parejas en orden determinista y sin repetidos.
    """
    parejas_unitarias: list[tuple[str, str]] = []
    for variable_origen in gramatica.variables:
        variables_alcanzadas = [variable_origen]  # Base: (A, A).
        pendientes = deque([variable_origen])
        while pendientes:
            variable_actual = pendientes.popleft()
            for cuerpo in gramatica.obtener_producciones(variable_actual):
                # Inducción: (A, B) y B -> C unitaria dan (A, C).
                if es_produccion_unitaria(gramatica, cuerpo) and cuerpo[0] not in variables_alcanzadas:
                    variables_alcanzadas.append(cuerpo[0])
                    pendientes.append(cuerpo[0])
        parejas_unitarias.extend(
            (variable_origen, variable_alcanzada) for variable_alcanzada in variables_alcanzadas
        )
    return parejas_unitarias


def eliminar_producciones_unitarias(gramatica: Gramatica) -> Gramatica:
    """Construye una gramática equivalente sin producciones unitarias.

    Para cada pareja unitaria (A, B), en orden, se agregan a A todos los
    cuerpos no unitarios de B (sin duplicar).

    Parámetros:
        gramatica: gramática original (no se modifica).

    Retorna:
        Una gramática nueva sin producciones A -> B, con las variables en el mismo orden.
    """
    gramatica_sin_unitarias = Gramatica(gramatica.simbolo_inicial)
    for variable in gramatica.variables:
        gramatica_sin_unitarias.agregar_variable(variable)
    for variable_cabeza, variable_destino in calcular_parejas_unitarias(gramatica):
        for cuerpo in gramatica.obtener_producciones(variable_destino):
            if not es_produccion_unitaria(gramatica, cuerpo):
                gramatica_sin_unitarias.agregar_produccion(variable_cabeza, cuerpo)
    return gramatica_sin_unitarias
