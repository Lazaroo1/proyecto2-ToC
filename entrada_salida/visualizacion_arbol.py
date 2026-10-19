"""Representaciones del árbol sintáctico para mostrar sus derivaciones."""

import json
import shutil
import subprocess
from pathlib import Path

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


def arbol_a_dot(raiz: NodoArbol) -> str:
    """Genera DOT con identificadores en preorden y etiquetas escapadas."""
    lineas = ['digraph ArbolSintactico {', '  graph [ordering="out"];',
              '  node [fontname="Helvetica", style="filled"];']
    siguiente_identificador = 0

    def agregar_nodo(nodo: NodoArbol) -> str:
        nonlocal siguiente_identificador
        identificador = f"n{siguiente_identificador}"
        siguiente_identificador += 1
        forma, color = ("box", "#fff2cc") if nodo.es_hoja() else ("ellipse", "#d9eaf7")
        etiqueta = json.dumps(nodo.simbolo, ensure_ascii=False)
        lineas.append(f'  {identificador} [label={etiqueta}, shape={forma}, fillcolor="{color}"];')
        for hijo in nodo.hijos:
            identificador_hijo = agregar_nodo(hijo)
            lineas.append(f"  {identificador} -> {identificador_hijo};")
        return identificador

    agregar_nodo(raiz)
    return "\n".join([*lineas, "}"])


def buscar_ejecutable_dot() -> str | None:
    """Busca Graphviz en PATH y en sus ubicaciones habituales de Windows."""
    ejecutable = shutil.which("dot")
    if ejecutable:
        return ejecutable
    for carpeta in ("C:/Program Files", "C:/Program Files (x86)"):
        ruta = Path(carpeta) / "Graphviz" / "bin" / "dot.exe"
        if ruta.is_file():
            return str(ruta)
    return None


def exportar_arbol_imagen(raiz: NodoArbol, ruta_base: Path, formato: str = "png") -> Path | None:
    """Guarda siempre DOT y devuelve la imagen si Graphviz está disponible."""
    ruta_base = Path(ruta_base)
    ruta_base.parent.mkdir(parents=True, exist_ok=True)
    ruta_dot = ruta_base.with_suffix(".dot")
    ruta_dot.write_text(arbol_a_dot(raiz), encoding="utf-8")
    ejecutable = buscar_ejecutable_dot()
    if ejecutable is None:
        return None
    ruta_imagen = ruta_base.with_suffix(f".{formato}")
    subprocess.run([ejecutable, f"-T{formato}", str(ruta_dot), "-o", str(ruta_imagen)],
                   check=True, capture_output=True)
    return ruta_imagen
