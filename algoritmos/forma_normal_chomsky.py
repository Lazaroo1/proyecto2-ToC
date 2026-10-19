"""Forma Normal de Chomsky (CNF), según Hopcroft §7.1.5.

Una gramática está en CNF si toda producción tiene una de estas formas:

- A -> B C, con B y C variables, o
- A -> a, con a un terminal.

Una gramática en CNF no puede generar la cadena vacía. Si ε pertenecía al
lenguaje original, se recuerda aparte (genera_cadena_vacia) y CYK acepta la
frase vacía por separado.

Construcción (a): para cada terminal a que aparece en un cuerpo de longitud 2
o más, se crea una variable nueva A con una única producción A -> a, y se usa
A en lugar de a en esos cuerpos.
"""

from __future__ import annotations

from modelos.gramatica import Cuerpo, Gramatica

NOMBRES_MNEMOTECNICOS: dict[str, str] = {"(": "L", ")": "R", "+": "P", "*": "M", "0": "Z", "1": "O"}
"""Nombres del libro para las variables de algunos terminales (L = left, R = right, P = plus...)."""

LETRAS_PARA_VARIABLES_NUEVAS = "ZYXWVUTSRQPONMLKJIHGFEDCBA"
"""Orden en que se prueban las letras para variables nuevas (desde la Z hacia atrás)."""

PREFIJO_VARIABLES_NUMERADAS = "C"
"""Prefijo de las variables nuevas cuando ya no quedan letras libres: C1, C2, …"""


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


def generar_nombre_variable_nueva(nombres_usados: set[str]) -> str:
    """Elige un nombre libre para una variable nueva y lo marca como usado.

    Prueba las letras de la Z a la A; si todas están ocupadas, usa C1, C2, …

    Parámetros:
        nombres_usados: nombres de variables y terminales ya existentes (se modifica).

    Retorna:
        El nombre elegido.
    """
    for letra in LETRAS_PARA_VARIABLES_NUEVAS:
        if letra not in nombres_usados:
            nombres_usados.add(letra)
            return letra
    numero = 1
    while f"{PREFIJO_VARIABLES_NUMERADAS}{numero}" in nombres_usados:
        numero += 1
    nombre_numerado = f"{PREFIJO_VARIABLES_NUMERADAS}{numero}"
    nombres_usados.add(nombre_numerado)
    return nombre_numerado


def generar_nombre_variable_para_terminal(terminal: str, nombres_usados: set[str]) -> str:
    """Elige el nombre de la variable que reemplazará a un terminal y lo marca como usado.

    Primero intenta el nombre mnemotécnico del libro ("(" -> L, "+" -> P...);
    si no hay y el terminal empieza con letra, esa letra en mayúscula
    ("a" -> A, "id" -> I). Si el candidato no existe o ya está ocupado, usa
    generar_nombre_variable_nueva.

    Parámetros:
        terminal: terminal que se va a reemplazar.
        nombres_usados: nombres ya existentes (se modifica).

    Retorna:
        El nombre elegido.
    """
    nombre_candidato = NOMBRES_MNEMOTECNICOS.get(terminal)
    if nombre_candidato is None and terminal[:1].isalpha():
        nombre_candidato = terminal[0].upper()
    if nombre_candidato is not None and nombre_candidato not in nombres_usados:
        nombres_usados.add(nombre_candidato)
        return nombre_candidato
    return generar_nombre_variable_nueva(nombres_usados)


def reemplazar_terminales_en_cuerpos_largos(gramatica: Gramatica) -> tuple[Gramatica, dict[str, str]]:
    """Construcción (a) de CNF: saca los terminales de los cuerpos de longitud ≥ 2.

    Se recorren las variables y sus cuerpos en orden. La primera vez que un
    terminal aparece en un cuerpo largo se crea su variable; las siguientes
    veces se reutiliza. Los cuerpos de longitud 1 no se tocan. Las variables
    nuevas se agregan al final, en orden de creación.

    Parámetros:
        gramatica: gramática sin producciones ε ni unitarias (no se modifica).

    Retorna:
        La gramática nueva y el diccionario terminal -> variable nueva, en orden de creación.
    """
    nombres_usados = set(gramatica.variables) | set(gramatica.terminales)
    variable_por_terminal: dict[str, str] = {}
    gramatica_resultante = Gramatica(gramatica.simbolo_inicial)
    for variable in gramatica.variables:
        gramatica_resultante.agregar_variable(variable)

    for variable in gramatica.variables:
        for cuerpo in gramatica.obtener_producciones(variable):
            if len(cuerpo) < 2:
                gramatica_resultante.agregar_produccion(variable, cuerpo)
                continue
            cuerpo_solo_con_variables: list[str] = []
            for simbolo in cuerpo:
                if gramatica.es_variable(simbolo):
                    cuerpo_solo_con_variables.append(simbolo)
                    continue
                if simbolo not in variable_por_terminal:
                    variable_por_terminal[simbolo] = generar_nombre_variable_para_terminal(
                        simbolo, nombres_usados
                    )
                cuerpo_solo_con_variables.append(variable_por_terminal[simbolo])
            gramatica_resultante.agregar_produccion(variable, tuple(cuerpo_solo_con_variables))

    for terminal, variable_nueva in variable_por_terminal.items():
        gramatica_resultante.agregar_produccion(variable_nueva, (terminal,))
    return gramatica_resultante, variable_por_terminal


def _es_produccion_en_cnf(gramatica: Gramatica, cuerpo: Cuerpo) -> bool:
    """Un cuerpo válido es un solo terminal o exactamente dos variables."""
    if len(cuerpo) == 1:
        return not gramatica.es_variable(cuerpo[0])
    if len(cuerpo) == 2:
        return all(gramatica.es_variable(simbolo) for simbolo in cuerpo)
    return False
