"""Presentación determinista de la tabla de programación dinámica."""

from algoritmos.cyk import ResultadoCYK


def tabla_cyk_a_texto(resultado: ResultadoCYK, orden_variables: list[str]) -> str:
    """Muestra el triángulo por longitud descendente y posición inicial."""
    cantidad = len(resultado.tokens)
    if cantidad == 0:
        return "Tabla CYK: la frase está vacía."
    filas: list[list[str]] = []
    for longitud in range(cantidad, 0, -1):
        celdas = []
        for inicio in range(cantidad - longitud + 1):
            celda = resultado.tabla[inicio][inicio + longitud - 1]
            variables = [variable for variable in orden_variables if variable in celda]
            celdas.append("{" + ", ".join(variables) + "}" if celda else "∅")
        filas.append(celdas)
    ancho = max(len(texto) for texto in [*resultado.tokens,
                                        *(celda for fila in filas for celda in fila)])
    digitos = len(str(cantidad))
    lineas = ["Tabla CYK (fila = longitud de la subcadena, columna = posición inicial):"]
    for longitud, celdas in zip(range(cantidad, 0, -1), filas):
        lineas.append(f"{longitud:>{digitos}} │ "
                      + "  ".join(celda.ljust(ancho) for celda in celdas).rstrip())
    lineas.append(" " * digitos + " │ "
                  + "  ".join(token.ljust(ancho) for token in resultado.tokens).rstrip())
    return "\n".join(lineas)


def formatear_resultado(frase: str, tokens: list[str], tokens_desconocidos: list[str],
                       acepta: bool) -> str:
    """Muestra frase, tokens, aviso opcional y decisión de pertenencia."""
    lineas = [f"Frase: {frase}", f"Tokens ({len(tokens)}): {' | '.join(tokens)}"]
    if tokens_desconocidos:
        lineas.append("Aviso: estas palabras no son terminales de la gramática: "
                      + ", ".join(tokens_desconocidos))
    decision = "SÍ — la frase pertenece" if acepta else "NO — la frase no pertenece"
    lineas.append(f"Resultado: {decision} al lenguaje de la gramática.")
    return "\n".join(lineas)
