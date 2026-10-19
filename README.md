# Proyecto 2 — Simplificación de gramáticas y algoritmo CYK

Proyecto 2 del curso **Teoría de la Computación**.

El programa recibe una gramática libre de contexto (que puede estar o no en Forma Normal de Chomsky), la simplifica y la convierte a **CNF**. Después usa el algoritmo **CYK** (programación dinámica) para decidir si una frase pertenece al lenguaje: responde **SÍ** o **NO**, indica el **tiempo** que tardó la validación y construye el **parse tree** de la frase.

## Integrantes

| Integrante | Carnet |
|---|---|
| Lázaro ([@Lazaroo1](https://github.com/Lazaroo1)) | _por agregar_ |
| Jorge Villeda | 24932 |

## Requisitos

- Python 3.10 o superior (solo la biblioteca estándar).

## Formato de las gramáticas

Las gramáticas se escriben en archivos `.txt` dentro de [`gramaticas/`](gramaticas/):

- Una producción por línea: `CABEZA -> cuerpo1 | cuerpo2 | ...` (también se acepta la flecha `→`).
- **Los símbolos van separados por espacios**: `( E )` y no `(E)`. Un terminal puede tener varias letras (`id`, `cooks`).
- `e` (o `ε`) representa la cadena vacía. `e` queda reservado y no puede ser terminal.
- **Variable**: todo símbolo que aparece como cabeza, o que empieza con mayúscula aunque no tenga producciones. **Terminal**: todo lo demás.
- El **símbolo inicial** es la cabeza de la primera producción.
- Una misma cabeza puede aparecer en varias líneas; sus producciones se juntan.
- Las líneas vacías y las que empiezan con `#` se ignoran.

| Archivo | Descripción |
|---|---|
| `ingles.txt` | Gramática del inglés del enunciado (ya está en CNF). |
| `1.txt` | Gramática de expresiones del catedrático (no está en CNF). |
| `1-cnf.txt` | La misma gramática en CNF, según el catedrático (resultado esperado). |
| `expresiones_recursiva.txt` | Expresiones con recursión por la izquierda (origen de `1.txt`). |
| `hopcroft_epsilon.txt` | Ejemplo del libro para eliminar producciones ε. |
| `hopcroft_unitarias.txt` | Ejemplo del libro para eliminar producciones unitarias y convertir a CNF. |
| `inutiles.txt` | Ejemplo del libro para eliminar símbolos inútiles. |
| `anbn.txt` | aⁿbⁿ con n ≥ 0: la cadena vacía sí pertenece al lenguaje. |

## Estado

En desarrollo.
