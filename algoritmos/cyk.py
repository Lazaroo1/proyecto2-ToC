"""Reconocimiento de cadenas en CNF mediante programación dinámica."""

from dataclasses import dataclass

from algoritmos.forma_normal_chomsky import es_forma_normal_chomsky
from modelos.gramatica import Gramatica


@dataclass
class ResultadoCYK:
    """Tokens, tabla de intervalos inclusivos y decisión de pertenencia."""

    tokens: list[str]
    tabla: list[list[set[str]]]
    acepta: bool


def cyk(gramatica_cnf: Gramatica, tokens: list[str],
        genera_cadena_vacia: bool = False) -> ResultadoCYK:
    """Determina si los tokens pertenecen al lenguaje sin modificar las entradas.

    X[inicio][fin] contiene las variables que derivan ese intervalo inclusivo.
    Base: A -> token. Recurrencia: A -> B C aporta A si B y C derivan los
    intervalos separados por algún corte. Se llena por longitud creciente,
    después inicio, corte y producción en orden de la gramática.
    Tiempo O(n³·|R|); memoria O(n²·|V|). La cadena vacía se trata aparte.
    """
    if not es_forma_normal_chomsky(gramatica_cnf):
        raise ValueError("CYK requiere una gramática en Forma Normal de Chomsky (CNF).")
    variables_por_terminal: dict[str, list[str]] = {}
    producciones_binarias: list[tuple[str, str, str]] = []
    for cabeza, cuerpos in gramatica_cnf.producciones.items():
        for cuerpo in cuerpos:
            if len(cuerpo) == 1:
                variables_por_terminal.setdefault(cuerpo[0], []).append(cabeza)
            else:
                producciones_binarias.append((cabeza, *cuerpo))
    cantidad_tokens = len(tokens)
    tabla = [[set() for columna in tokens] for fila in tokens]
    if not tokens:
        return ResultadoCYK(list(tokens), tabla, genera_cadena_vacia)
    for posicion, token in enumerate(tokens):
        tabla[posicion][posicion].update(variables_por_terminal.get(token, []))
    for longitud in range(2, cantidad_tokens + 1):
        for inicio in range(cantidad_tokens - longitud + 1):
            fin = inicio + longitud - 1
            for corte in range(inicio, fin):
                for cabeza, izquierda, derecha in producciones_binarias:
                    if izquierda in tabla[inicio][corte] and derecha in tabla[corte + 1][fin]:
                        tabla[inicio][fin].add(cabeza)
    acepta = gramatica_cnf.simbolo_inicial in tabla[0][cantidad_tokens - 1]
    return ResultadoCYK(list(tokens), tabla, acepta)
