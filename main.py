"""Punto de entrada del proyecto (consola).

Lee una gramática libre de contexto, la simplifica y la convierte a Forma
Normal de Chomsky (CNF) mostrando el paso a paso. Después valida frases con el
algoritmo CYK: responde SÍ/NO, mide el tiempo de validación y muestra la tabla
de programación dinámica y el parse tree (en consola y como imagen con Graphviz).

Uso:
    python main.py                                         # gramática del inglés, modo interactivo
    python main.py -f "She eats a cake with a fork"        # validar una frase y terminar
    python main.py -g gramaticas/1.txt -f "(id*id)+id"     # CYK sobre otra gramática
    python main.py -f "he cooks" --repeticiones 1000       # tiempo promedio de CYK
    python main.py -g gramaticas/1.txt --sin-pasos         # solo la gramática original y la CNF
    python main.py -g gramaticas/1.txt --guardar-cnf salidas/1-cnf.txt
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import time
from pathlib import Path

from algoritmos.forma_normal_chomsky import ResultadoConversionCNF, convertir_a_cnf
from algoritmos.cyk import construir_arbol_sintactico, contar_arboles_de_derivacion, cyk
from entrada_salida.escritor_gramatica import guardar_gramatica_en_archivo
from entrada_salida.formato_pasos import formatear_conversion, formatear_gramatica_con_titulo
from entrada_salida.lector_gramatica import ErrorFormatoGramatica, leer_gramatica_desde_archivo
from entrada_salida.formato_cyk import formatear_resultado, formatear_tiempo, tabla_cyk_a_texto
from entrada_salida.tokenizador import encontrar_tokens_desconocidos, tokenizar_frase
from entrada_salida.visualizacion_arbol import (
    arbol_a_corchetes, arbol_a_texto, exportar_arbol_imagen,
)

CARPETA_DEL_PROYECTO = Path(__file__).resolve().parent
RUTA_GRAMATICA_POR_DEFECTO = CARPETA_DEL_PROYECTO / "gramaticas" / "ingles.txt"
MILISEGUNDOS_POR_SEGUNDO = 1000


def configurar_consola_utf8() -> None:
    """Hace que la consola acepte ε, │ y ├── aunque Windows use otra codificación."""
    for flujo_de_salida in (sys.stdout, sys.stderr):
        if hasattr(flujo_de_salida, "reconfigure"):
            flujo_de_salida.reconfigure(encoding="utf-8")


def construir_analizador_argumentos() -> argparse.ArgumentParser:
    """Define los argumentos de la línea de comandos."""
    analizador = argparse.ArgumentParser(
        prog="main.py",
        description=(
            "Simplifica una gramática libre de contexto, la convierte a Forma Normal "
            "de Chomsky (CNF) mostrando el paso a paso y valida frases con el algoritmo "
            "CYK: responde SÍ/NO, mide el tiempo y construye el parse tree. Sin -f, "
            "pide frases en modo interactivo hasta escribir 'salir'."
        ),
    )
    analizador.add_argument(
        "-g",
        "--gramatica",
        type=Path,
        default=RUTA_GRAMATICA_POR_DEFECTO,
        metavar="RUTA",
        help="archivo .txt con la gramática (por defecto: gramaticas/ingles.txt)",
    )
    analizador.add_argument(
        "--sin-pasos",
        action="store_true",
        help="mostrar solo la gramática original y la gramática en CNF",
    )
    analizador.add_argument(
        "--guardar-cnf",
        type=Path,
        metavar="RUTA",
        help="guardar la gramática en CNF en ese archivo",
    )
    analizador.add_argument("-f", "--frase", metavar="TEXTO", help="frase que se desea validar")
    analizador.add_argument("--sin-tabla", action="store_true", help="omitir la tabla CYK")
    analizador.add_argument("--sin-imagen", action="store_true", help="omitir la exportación del árbol")
    analizador.add_argument("--salida", type=Path, default=CARPETA_DEL_PROYECTO / "salidas",
                            metavar="CARPETA", help="carpeta para los árboles exportados")
    analizador.add_argument("--repeticiones", type=int, default=1, metavar="N",
                            help="cantidad positiva de ejecuciones de CYK para medir su tiempo")
    return analizador


def cargar_y_convertir(ruta_gramatica: Path) -> tuple[ResultadoConversionCNF, float]:
    """Lee la gramática y la convierte a CNF.

    Parámetros:
        ruta_gramatica: archivo .txt con la gramática.

    Retorna:
        El resultado de la conversión y cuánto tardó convertir_a_cnf, en milisegundos.
    """
    gramatica = leer_gramatica_desde_archivo(ruta_gramatica)
    instante_inicial = time.perf_counter()
    resultado = convertir_a_cnf(gramatica)
    tiempo_milisegundos = (time.perf_counter() - instante_inicial) * MILISEGUNDOS_POR_SEGUNDO
    return resultado, tiempo_milisegundos


def mostrar_conversion(
    resultado: ResultadoConversionCNF, tiempo_milisegundos: float, mostrar_pasos: bool
) -> None:
    """Imprime el paso a paso (o solo la gramática original y la CNF) y el tiempo."""
    if mostrar_pasos:
        print(formatear_conversion(resultado))
    else:
        print(formatear_gramatica_con_titulo("GRAMÁTICA ORIGINAL", resultado.gramatica_original))
        print()
        print(formatear_gramatica_con_titulo("GRAMÁTICA EN CNF", resultado.gramatica_cnf))
    print()
    print(f"Tiempo de conversión a CNF: {tiempo_milisegundos:.4f} ms")


def obtener_ruta_legible(ruta: Path) -> str:
    """Devuelve la ruta relativa a la carpeta actual si se puede (más corta de leer)."""
    try:
        return str(ruta.resolve().relative_to(Path.cwd()))
    except ValueError:
        return str(ruta)


def analizar_frase(frase: str, conversion: ResultadoConversionCNF,
                   argumentos: argparse.Namespace) -> None:
    """Tokeniza, reconoce y presenta la tabla y el árbol de una frase."""
    gramatica = conversion.gramatica_cnf
    tokens = tokenizar_frase(frase, gramatica.terminales)
    tiempos: list[float] = []
    for repeticion in range(argumentos.repeticiones):
        instante_inicial = time.perf_counter()
        resultado = cyk(gramatica, tokens, conversion.genera_cadena_vacia)
        instante_final = time.perf_counter()
        tiempos.append((instante_final - instante_inicial) * MILISEGUNDOS_POR_SEGUNDO)
    desconocidos = encontrar_tokens_desconocidos(tokens, gramatica.terminales)
    print(formatear_resultado(frase, tokens, desconocidos, resultado.acepta))
    print(formatear_tiempo(sum(tiempos) / len(tiempos), len(tiempos), min(tiempos)))
    if not argumentos.sin_tabla:
        print(tabla_cyk_a_texto(resultado, gramatica.variables))
    arbol = construir_arbol_sintactico(resultado, gramatica.simbolo_inicial)
    if arbol is None:
        return
    cantidad_arboles = contar_arboles_de_derivacion(gramatica, tokens, conversion.genera_cadena_vacia)
    aviso = (" (la frase es ambigua en esta gramática; se muestra el primero)"
             if cantidad_arboles > 1 else "")
    print(f"Árboles de derivación: {cantidad_arboles}{aviso}")
    print("Parse tree:")
    print(arbol_a_texto(arbol))
    print("Notación con corchetes:")
    print(arbol_a_corchetes(arbol))
    if not argumentos.sin_imagen:
        nombre = re.sub(r"[^\w]+", "_", "_".join(tokens).lower(), flags=re.ASCII).strip("_")
        nombre = nombre[:60] or "arbol"
        ruta_base = argumentos.salida / f"arbol_{nombre}"
        try:
            imagen = exportar_arbol_imagen(arbol, ruta_base)
            if imagen is None:
                print("Graphviz no está instalado. Archivo DOT: "
                      + obtener_ruta_legible(ruta_base.with_suffix(".dot")))
            else:
                print(f"Imagen del árbol: {obtener_ruta_legible(imagen)}")
        except (OSError, subprocess.CalledProcessError) as error:
            print(f"No se pudo exportar la imagen del árbol: {error}", file=sys.stderr)


def main(argumentos_linea: list[str] | None = None) -> int:
    """Ejecuta el programa.

    Parámetros:
        argumentos_linea: argumentos a usar en lugar de sys.argv (útil en pruebas).

    Retorna:
        El código de salida: 0 si todo salió bien, 1 si hubo un error con la gramática.
    """
    configurar_consola_utf8()
    analizador = construir_analizador_argumentos()
    argumentos = analizador.parse_args(argumentos_linea)
    if argumentos.repeticiones < 1:
        analizador.error("--repeticiones debe ser un entero mayor o igual a 1")
    ruta_legible = obtener_ruta_legible(argumentos.gramatica)

    try:
        resultado, tiempo_milisegundos = cargar_y_convertir(argumentos.gramatica)
    except FileNotFoundError:
        print(f"No se encontró el archivo de gramática: {ruta_legible}", file=sys.stderr)
        return 1
    except UnicodeDecodeError:
        print(f"El archivo {ruta_legible} no está guardado en UTF-8.", file=sys.stderr)
        return 1
    except OSError as error:
        print(f"No se pudo leer el archivo {ruta_legible}: {error}", file=sys.stderr)
        return 1
    except ErrorFormatoGramatica as error:
        print(f"Error de formato en {ruta_legible}: {error}", file=sys.stderr)
        return 1

    print(f"Gramática: {ruta_legible}")
    print()
    mostrar_conversion(resultado, tiempo_milisegundos, mostrar_pasos=not argumentos.sin_pasos)

    if argumentos.guardar_cnf is not None:
        guardar_gramatica_en_archivo(resultado.gramatica_cnf, argumentos.guardar_cnf)
        print(f"Gramática en CNF guardada en: {obtener_ruta_legible(argumentos.guardar_cnf)}")
    if argumentos.frase is not None:
        analizar_frase(argumentos.frase, resultado, argumentos)
    else:
        while True:
            try:
                frase = input("Escribe una frase (o 'salir' para terminar): ")
                if frase.strip().lower() == "salir":
                    break
                analizar_frase(frase, resultado, argumentos)
            except (EOFError, KeyboardInterrupt):
                print()
                break
    return 0


if __name__ == "__main__":
    sys.exit(main())
