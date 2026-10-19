"""Modelo de datos de una gramática libre de contexto (CFG).

Una gramática G = (V, T, P, S) se guarda como un diccionario que va de cada
variable a la lista de sus cuerpos. Tanto las variables como los cuerpos
conservan su orden de inserción, para que todas las salidas del programa sean
deterministas. Los terminales no se guardan aparte: son los símbolos de los
cuerpos que no son variables.
"""

from __future__ import annotations

Cuerpo = tuple[str, ...]
"""Cuerpo de una producción: tupla de símbolos. La tupla vacía () representa ε."""


class Gramatica:
    """Gramática libre de contexto con símbolo inicial y producciones ordenadas.

    Atributos:
        simbolo_inicial: variable desde la que se generan las cadenas.
        producciones: variable -> lista de cuerpos, sin duplicados y en orden
            de inserción. Una variable puede tener la lista vacía.
    """

    def __init__(self, simbolo_inicial: str) -> None:
        """Crea una gramática vacía cuya primera variable es el símbolo inicial.

        Parámetros:
            simbolo_inicial: nombre de la variable inicial.
        """
        self.simbolo_inicial = simbolo_inicial
        self.producciones: dict[str, list[Cuerpo]] = {simbolo_inicial: []}

    @property
    def variables(self) -> list[str]:
        """Variables de la gramática, en orden de inserción."""
        return list(self.producciones)

    @property
    def terminales(self) -> list[str]:
        """Símbolos de los cuerpos que no son variables, en orden de primera aparición."""
        terminales_en_orden: dict[str, None] = {}
        for cuerpos in self.producciones.values():
            for cuerpo in cuerpos:
                for simbolo in cuerpo:
                    if simbolo not in self.producciones:
                        terminales_en_orden.setdefault(simbolo, None)
        return list(terminales_en_orden)

    def agregar_variable(self, variable: str) -> None:
        """Registra una variable (sin producciones) si todavía no existe.

        Parámetros:
            variable: nombre de la variable.
        """
        self.producciones.setdefault(variable, [])

    def agregar_produccion(self, cabeza: str, cuerpo: Cuerpo) -> None:
        """Agrega la producción cabeza -> cuerpo sin duplicarla.

        Si la cabeza todavía no es variable, se registra.

        Parámetros:
            cabeza: variable del lado izquierdo.
            cuerpo: símbolos del lado derecho; () representa ε.
        """
        cuerpos_de_la_cabeza = self.producciones.setdefault(cabeza, [])
        cuerpo_como_tupla = tuple(cuerpo)
        if cuerpo_como_tupla not in cuerpos_de_la_cabeza:
            cuerpos_de_la_cabeza.append(cuerpo_como_tupla)

    def eliminar_variable(self, variable: str) -> None:
        """Quita una variable y todo cuerpo (de cualquier variable) que la contenga.

        Parámetros:
            variable: variable a eliminar.

        Lanza:
            ValueError: si se intenta eliminar el símbolo inicial.
        """
        if variable == self.simbolo_inicial:
            raise ValueError(f"No se puede eliminar el símbolo inicial '{variable}'.")
        self.producciones.pop(variable, None)
        for cabeza, cuerpos in self.producciones.items():
            self.producciones[cabeza] = [cuerpo for cuerpo in cuerpos if variable not in cuerpo]

    def obtener_producciones(self, variable: str) -> list[Cuerpo]:
        """Devuelve una copia de los cuerpos de una variable (lista vacía si no tiene).

        Parámetros:
            variable: variable consultada.

        Retorna:
            Lista de cuerpos en orden de inserción.
        """
        return list(self.producciones.get(variable, []))

    def es_variable(self, simbolo: str) -> bool:
        """Indica si el símbolo es una variable de la gramática."""
        return simbolo in self.producciones

    def es_terminal(self, simbolo: str) -> bool:
        """Indica si el símbolo es un terminal de la gramática (aparece en un cuerpo y no es variable)."""
        return not self.es_variable(simbolo) and simbolo in self.terminales

    def contar_producciones(self) -> int:
        """Cantidad total de producciones (cada alternativa cuenta como una)."""
        return sum(len(cuerpos) for cuerpos in self.producciones.values())

    def copiar(self) -> Gramatica:
        """Devuelve una copia independiente: cambiar la copia no afecta a la original."""
        copia = Gramatica(self.simbolo_inicial)
        copia.producciones = {
            variable: list(cuerpos) for variable, cuerpos in self.producciones.items()
        }
        return copia

    def __eq__(self, otra: object) -> bool:
        """Dos gramáticas son iguales si tienen el mismo símbolo inicial y las mismas producciones.

        Se ignora el orden de variables y cuerpos, y también las variables sin producciones.
        """
        if not isinstance(otra, Gramatica):
            return NotImplemented
        return (
            self.simbolo_inicial == otra.simbolo_inicial
            and self._producciones_como_conjuntos() == otra._producciones_como_conjuntos()
        )

    def _producciones_como_conjuntos(self) -> dict[str, frozenset[Cuerpo]]:
        """Producciones sin orden, solo de las variables que tienen al menos un cuerpo."""
        return {
            variable: frozenset(cuerpos)
            for variable, cuerpos in self.producciones.items()
            if cuerpos
        }

    def __repr__(self) -> str:
        return (
            f"Gramatica(simbolo_inicial={self.simbolo_inicial!r}, "
            f"variables={self.variables}, producciones={self.contar_producciones()})"
        )
