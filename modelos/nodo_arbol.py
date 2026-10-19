"""Nodos del árbol sintáctico con hijos ordenados de izquierda a derecha."""

from dataclasses import dataclass, field


@dataclass
class NodoArbol:
    """Símbolo de una derivación y sus subárboles."""

    simbolo: str
    hijos: list["NodoArbol"] = field(default_factory=list)

    def es_hoja(self) -> bool:
        """Indica si no tiene hijos."""
        return not self.hijos

    def obtener_hojas(self) -> list[str]:
        """Devuelve los terminales en orden de lectura."""
        if self.es_hoja():
            return [self.simbolo]
        return [hoja for hijo in self.hijos for hoja in hijo.obtener_hojas()]

    def calcular_altura(self) -> int:
        """Cuenta aristas del camino más largo; una hoja tiene altura cero."""
        return 1 + max((hijo.calcular_altura() for hijo in self.hijos), default=-1)

    def contar_nodos(self) -> int:
        """Cuenta la raíz y todos sus descendientes."""
        return 1 + sum(hijo.contar_nodos() for hijo in self.hijos)
