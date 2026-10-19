"""Representaciones del árbol sintáctico para mostrar sus derivaciones."""

from modelos.nodo_arbol import NodoArbol


def arbol_a_texto(raiz: NodoArbol) -> str:
    """Dibuja las ramas conservando el orden de los hijos, sin salto final."""
    lineas = [raiz.simbolo]

    def agregar_hijos(nodo: NodoArbol, prefijo: str) -> None:
        for posicion, hijo in enumerate(nodo.hijos):
            es_ultimo = posicion == len(nodo.hijos) - 1
            lineas.append(prefijo + ("└── " if es_ultimo else "├── ") + hijo.simbolo)
            agregar_hijos(hijo, prefijo + ("    " if es_ultimo else "│   "))

    agregar_hijos(raiz, "")
    return "\n".join(lineas)


def arbol_a_corchetes(raiz: NodoArbol) -> str:
    """Representa hojas como símbolos y nodos internos entre corchetes."""
    if raiz.es_hoja():
        return raiz.simbolo
    return f"[{raiz.simbolo} {' '.join(arbol_a_corchetes(hijo) for hijo in raiz.hijos)}]"
