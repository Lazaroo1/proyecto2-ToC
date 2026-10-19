"""Forma Normal de Chomsky (CNF), según Hopcroft §7.1.5.

Una gramática está en CNF si toda producción tiene una de estas formas:

- A -> B C, con B y C variables, o
- A -> a, con a un terminal.

Una gramática en CNF no puede generar la cadena vacía. Si ε pertenecía al
lenguaje original, se recuerda aparte (genera_cadena_vacia) y CYK acepta la
frase vacía por separado.
"""

from __future__ import annotations

from modelos.gramatica import Cuerpo, Gramatica


def obtener_producciones_fuera_de_cnf(gramatica: Gramatica) -> list[tuple[str, Cuerpo]]:
    """Lista, en orden, las producciones que no cumplen la CNF.

    Quedan fuera de CNF las producciones ε, las unitarias (A -> B), las mixtas
    (A -> a B) y las largas (A -> B C D).

    Parámetros:
        gramatica: gramática a revisar.

    Retorna:
        Pares (cabeza, cuerpo) de las producciones inválidas.
    """
    producciones_invalidas: list[tuple[str, Cuerpo]] = []
    for variable in gramatica.variables:
        for cuerpo in gramatica.obtener_producciones(variable):
            if not _es_produccion_en_cnf(gramatica, cuerpo):
                producciones_invalidas.append((variable, cuerpo))
    return producciones_invalidas


def es_forma_normal_chomsky(gramatica: Gramatica) -> bool:
    """Indica si todas las producciones son A -> B C o A -> a.

    Parámetros:
        gramatica: gramática a revisar.

    Retorna:
        True si la gramática está en CNF.
    """
    return not obtener_producciones_fuera_de_cnf(gramatica)


def _es_produccion_en_cnf(gramatica: Gramatica, cuerpo: Cuerpo) -> bool:
    """Un cuerpo válido es un solo terminal o exactamente dos variables."""
    if len(cuerpo) == 1:
        return not gramatica.es_variable(cuerpo[0])
    if len(cuerpo) == 2:
        return all(gramatica.es_variable(simbolo) for simbolo in cuerpo)
    return False
