"""Tokenización de palabras y expresiones según el vocabulario de la gramática."""

from collections.abc import Iterable

SIGNOS_DE_PUNTUACION = ".,;:!?¡¿\"'"


def tokenizar_frase(frase: str, terminales: Iterable[str]) -> list[str]:
    """Reconoce fragmentos completos antes de quitar puntuación o segmentarlos.

    La segmentación usa programación dinámica y prioriza terminales largos.
    Las palabras alfanuméricas desconocidas se conservan si hay terminales largos.
    """
    vocabulario = set(terminales)
    ordenados = sorted(vocabulario - {""}, key=lambda terminal: (-len(terminal), terminal))
    son_caracteres = bool(ordenados) and all(len(terminal) == 1 for terminal in ordenados)

    def reconocer(fragmento: str) -> list[str] | None:
        for variante in dict.fromkeys((fragmento, fragmento.lower())):
            if variante in vocabulario:
                return [variante]
        if not son_caracteres and fragmento.isalnum():
            return None
        for variante in dict.fromkeys((fragmento, fragmento.lower())):
            particiones: dict[int, list[str]] = {len(variante): []}
            for posicion in range(len(variante) - 1, -1, -1):
                for terminal in ordenados:
                    siguiente = posicion + len(terminal)
                    if variante.startswith(terminal, posicion) and siguiente in particiones:
                        particiones[posicion] = [terminal, *particiones[siguiente]]
                        break
            if 0 in particiones:
                return particiones[0]
        return None

    tokens: list[str] = []
    for fragmento in frase.split():
        reconocidos = reconocer(fragmento)
        if reconocidos is None:
            fragmento = fragmento.strip(SIGNOS_DE_PUNTUACION)
            if not fragmento:
                continue
            reconocidos = reconocer(fragmento)
        tokens.extend(reconocidos if reconocidos is not None else [fragmento.lower()])
    return tokens


def encontrar_tokens_desconocidos(tokens: list[str], terminales: Iterable[str]) -> list[str]:
    """Devuelve los desconocidos en orden de aparición y sin duplicarlos."""
    vocabulario = set(terminales)
    return list(dict.fromkeys(token for token in tokens if token not in vocabulario))
