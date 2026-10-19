"""Texto del paso a paso de la conversión a CNF, con el formato del ejemplo del catedrático.

Las funciones solo arman cadenas de texto; quien las llama (main.py) decide
dónde imprimirlas.
"""

from __future__ import annotations

from collections.abc import Iterable

from algoritmos.forma_normal_chomsky import PasoConversion, ResultadoConversionCNF
from entrada_salida.escritor_gramatica import describir_gramatica, gramatica_a_texto
from modelos.gramatica import Gramatica

TEXTO_NINGUNO = "ninguno"
TEXTO_NINGUNA = "ninguna"
TEXTO_SIN_CAMBIOS = "(sin cambios)"
TEXTO_SIN_PRODUCCIONES = "(la gramática no tiene producciones)"


def formatear_gramatica_con_titulo(titulo: str, gramatica: Gramatica) -> str:
    """Arma un bloque con encabezado, la gramática y su resumen.

    Parámetros:
        titulo: texto del encabezado (ej. "GRAMÁTICA ORIGINAL").
        gramatica: gramática a mostrar.

    Retorna:
        "══ titulo ══", las producciones y la línea de describir_gramatica.
    """
    return "\n".join(
        [
            f"══ {titulo} ══",
            gramatica_a_texto(gramatica) or TEXTO_SIN_PRODUCCIONES,
            describir_gramatica(gramatica),
        ]
    )


def formatear_conversion(resultado: ResultadoConversionCNF) -> str:
    """Arma el paso a paso completo de la conversión a CNF.

    Muestra la gramática original, cada paso con sus detalles (anulables,
    parejas unitarias, símbolos eliminados, variables nuevas) y la gramática
    que dejó, y al final la gramática en CNF. Si un paso no cambió nada se
    escribe "(sin cambios)".

    Parámetros:
        resultado: resultado de convertir_a_cnf.

    Retorna:
        El texto completo, con los bloques separados por una línea en blanco.
    """
    gramatica_original = resultado.gramatica_original
    orden_de_referencia = gramatica_original.variables + gramatica_original.terminales
    bloques = [formatear_gramatica_con_titulo("GRAMÁTICA ORIGINAL", gramatica_original)]

    gramatica_anterior = gramatica_original
    for numero_paso, paso in enumerate(resultado.pasos, start=1):
        lineas_del_paso = [f"── Paso {numero_paso}: {paso.titulo} ──"]
        lineas_del_paso.extend(_formatear_detalles(paso, orden_de_referencia))
        if paso.gramatica == gramatica_anterior:
            lineas_del_paso.append(TEXTO_SIN_CAMBIOS)
        else:
            lineas_del_paso.append(gramatica_a_texto(paso.gramatica) or TEXTO_SIN_PRODUCCIONES)
        bloques.append("\n".join(lineas_del_paso))
        gramatica_anterior = paso.gramatica

    bloques.append(formatear_gramatica_con_titulo("GRAMÁTICA EN CNF", resultado.gramatica_cnf))
    notas = _formatear_notas(resultado)
    if notas:
        bloques.append("\n".join(notas))
    return "\n\n".join(bloques)


def _formatear_detalles(paso: PasoConversion, orden_de_referencia: list[str]) -> list[str]:
    """Líneas con la información particular de cada paso."""
    detalles = paso.detalles
    if "anulables" in detalles:
        anulables = _unir_en_orden(detalles["anulables"], orden_de_referencia)
        return [f"Anulables: {anulables}"]
    if "parejas_unitarias" in detalles:
        parejas = ", ".join(
            f"({variable_cabeza}, {variable_destino})"
            for variable_cabeza, variable_destino in detalles["parejas_unitarias"]
        )
        return [f"Parejas unitarias: {parejas or TEXTO_NINGUNA}"]
    if "no_generadores" in detalles:
        return [
            f"No generadores: {_unir_en_orden(detalles['no_generadores'], orden_de_referencia)}",
            f"No alcanzables: {_unir_en_orden(detalles['no_alcanzables'], orden_de_referencia)}",
        ]
    if "variables_por_terminal" in detalles:
        variables_nuevas = ", ".join(
            f"{variable_nueva} -> {terminal}"
            for terminal, variable_nueva in detalles["variables_por_terminal"].items()
        )
        return [f"Variables nuevas: {variables_nuevas or TEXTO_NINGUNA}"]
    if "variables_por_cuerpo" in detalles:
        # Se muestra el cuerpo real de cada variable nueva (en sufijos de 3+ símbolos
        # el cuerpo es "primer símbolo + variable del resto").
        cuerpo_de_variable = {
            variable_nueva: " ".join(paso.gramatica.obtener_producciones(variable_nueva)[0])
            for variable_nueva in detalles["variables_por_cuerpo"].values()
        }
        variables_nuevas = ", ".join(
            f"{variable_nueva} -> {cuerpo}" for variable_nueva, cuerpo in cuerpo_de_variable.items()
        )
        return [f"Variables nuevas: {variables_nuevas or TEXTO_NINGUNA}"]
    return []


def _formatear_notas(resultado: ResultadoConversionCNF) -> list[str]:
    """Avisos finales: si ya estaba en CNF y si ε pertenece al lenguaje."""
    notas: list[str] = []
    if resultado.ya_estaba_en_cnf:
        if resultado.gramatica_cnf == resultado.gramatica_original:
            notas.append("La gramática ya estaba en CNF: la conversión no cambia nada.")
        else:
            notas.append("La gramática ya estaba en CNF; solo se eliminaron símbolos inútiles.")
    if resultado.genera_cadena_vacia:
        notas.append(
            "ε ∈ L(G): la frase vacía se acepta aparte, "
            "porque una gramática en CNF no puede generar ε."
        )
    return notas


def _unir_en_orden(simbolos: Iterable[str], orden_de_referencia: list[str]) -> str:
    """Une los símbolos con comas en el orden de la gramática (nunca en el orden de un set)."""
    posicion_de_simbolo = {simbolo: indice for indice, simbolo in enumerate(orden_de_referencia)}
    simbolos_ordenados = sorted(
        simbolos,
        key=lambda simbolo: (posicion_de_simbolo.get(simbolo, len(posicion_de_simbolo)), simbolo),
    )
    return ", ".join(simbolos_ordenados) or TEXTO_NINGUNO
