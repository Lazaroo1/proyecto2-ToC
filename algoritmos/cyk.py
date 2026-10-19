"""Reconocimiento de cadenas en CNF mediante programación dinámica."""

from dataclasses import dataclass, field

from algoritmos.forma_normal_chomsky import es_forma_normal_chomsky
from modelos.gramatica import Gramatica
from modelos.nodo_arbol import NodoArbol

Retroceso = str | tuple[int, str, str]


@dataclass
class ResultadoCYK:
    """Tokens, tabla de intervalos inclusivos y decisión de pertenencia."""

    tokens: list[str]
    tabla: list[list[set[str]]]
    acepta: bool
    retroceso: dict[tuple[int, int, str], Retroceso] = field(default_factory=dict)


def _precalcular_producciones(
    gramatica_cnf: Gramatica,
) -> tuple[dict[str, list[str]], list[tuple[str, str, str]]]:
    """Valida CNF y separa producciones terminales y binarias en su orden."""
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
    return variables_por_terminal, producciones_binarias


def cyk(gramatica_cnf: Gramatica, tokens: list[str],
        genera_cadena_vacia: bool = False) -> ResultadoCYK:
    """Determina si los tokens pertenecen al lenguaje sin modificar las entradas.

    X[inicio][fin] contiene las variables que derivan ese intervalo inclusivo.
    Base: A -> token. Recurrencia: A -> B C aporta A si B y C derivan los
    intervalos separados por algún corte. Se llena por longitud creciente,
    después inicio, corte y producción en orden de la gramática.
    Tiempo O(n³·|R|); memoria O(n²·|V|). La cadena vacía se trata aparte.
    """
    variables_por_terminal, producciones_binarias = _precalcular_producciones(gramatica_cnf)
    cantidad_tokens = len(tokens)
    retroceso: dict[tuple[int, int, str], Retroceso] = {}
    tabla = [[set() for columna in tokens] for fila in tokens]
    if not tokens:
        return ResultadoCYK(list(tokens), tabla, genera_cadena_vacia)
    for posicion, token in enumerate(tokens):
        tabla[posicion][posicion].update(variables_por_terminal.get(token, []))
        for cabeza in variables_por_terminal.get(token, []):
            retroceso.setdefault((posicion, posicion, cabeza), token)
    for longitud in range(2, cantidad_tokens + 1):
        for inicio in range(cantidad_tokens - longitud + 1):
            fin = inicio + longitud - 1
            for corte in range(inicio, fin):
                for cabeza, izquierda, derecha in producciones_binarias:
                    if izquierda in tabla[inicio][corte] and derecha in tabla[corte + 1][fin]:
                        tabla[inicio][fin].add(cabeza)
                        retroceso.setdefault((inicio, fin, cabeza), (corte, izquierda, derecha))
    acepta = gramatica_cnf.simbolo_inicial in tabla[0][cantidad_tokens - 1]
    return ResultadoCYK(list(tokens), tabla, acepta, retroceso)


def construir_arbol_sintactico(resultado: ResultadoCYK, simbolo_inicial: str) -> NodoArbol | None:
    """Reconstruye la primera derivación encontrada por CYK, sobre la CNF."""
    if not resultado.acepta:
        return None
    if not resultado.tokens:
        return NodoArbol(simbolo_inicial, [NodoArbol("ε")])

    def construir_nodo(inicio: int, fin: int, cabeza: str) -> NodoArbol:
        origen = resultado.retroceso[(inicio, fin, cabeza)]
        if isinstance(origen, str):
            return NodoArbol(cabeza, [NodoArbol(origen)])
        corte, izquierda, derecha = origen
        return NodoArbol(cabeza, [construir_nodo(inicio, corte, izquierda),
                                 construir_nodo(corte + 1, fin, derecha)])

    return construir_nodo(0, len(resultado.tokens) - 1, simbolo_inicial)


def contar_arboles_de_derivacion(gramatica_cnf: Gramatica, tokens: list[str],
                                genera_cadena_vacia: bool = False) -> int:
    """Cuenta derivaciones en la CNF sumando productos de conteos por corte.

    Para ε se devuelve la convención 1/0 según la bandera; no se cuentan las
    posibles derivaciones vacías de la gramática original.
    """
    variables_por_terminal, producciones_binarias = _precalcular_producciones(gramatica_cnf)
    if not tokens:
        return int(genera_cadena_vacia)
    cantidad = len(tokens)
    conteo: list[list[dict[str, int]]] = [[{} for columna in tokens] for fila in tokens]
    for posicion, token in enumerate(tokens):
        for cabeza in variables_por_terminal.get(token, []):
            conteo[posicion][posicion][cabeza] = conteo[posicion][posicion].get(cabeza, 0) + 1
    for longitud in range(2, cantidad + 1):
        for inicio in range(cantidad - longitud + 1):
            fin = inicio + longitud - 1
            for corte in range(inicio, fin):
                for cabeza, izquierda, derecha in producciones_binarias:
                    producto = (conteo[inicio][corte].get(izquierda, 0)
                                * conteo[corte + 1][fin].get(derecha, 0))
                    if producto:
                        conteo[inicio][fin][cabeza] = conteo[inicio][fin].get(cabeza, 0) + producto
    return conteo[0][cantidad - 1].get(gramatica_cnf.simbolo_inicial, 0)
