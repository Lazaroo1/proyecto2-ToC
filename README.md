# Proyecto 2 — Simplificación de gramáticas y algoritmo CYK

Proyecto 2 del curso **Teoría de la Computación**.

El programa recibe una gramática libre de contexto (que puede estar o no en Forma Normal de Chomsky), la simplifica y la convierte a **CNF**. Después usa el algoritmo **CYK** (programación dinámica) para decidir si una frase pertenece al lenguaje: responde **SÍ** o **NO**, indica el **tiempo** que tardó la validación y construye el **parse tree** de la frase.

## Integrantes

| Integrante | Carnet |
|---|---|
| Lázaro Díaz | 24713 |
| Jorge Villeda | 24932 |

## Requisitos

- Python 3.10 o superior (solo la biblioteca estándar).
- Graphviz opcional para generar imágenes PNG. Sin él se conserva DOT.

## Características

- Lectura de CFG, simplificación y conversión a CNF con los cinco pasos visibles.
- Reconocimiento CYK con resultado SÍ/NO, tabla triangular y aviso de palabras desconocidas.
- Tiempo de validación en milisegundos; promedio y mínimo con varias repeticiones.
- Parse tree en consola, corchetes y PNG/DOT; conteo de árboles para detectar ambigüedad.
- Modo interactivo y análisis de una frase desde argumentos.

## Instalación

```powershell
git clone https://github.com/Lazaroo1/proyecto2-ToC.git
cd proyecto2-ToC
python --version
python -m unittest discover -s pruebas -t . -v
```

No se necesita instalar paquetes con pip. Si `python` no está disponible,
instala Python 3.10 o superior y comprueba que su ejecutable esté en PATH.
La validación y las mediciones del reporte se realizaron con Python 3.13.13.

## Uso

Desde la raíz del proyecto:

```bash
python main.py                                    # inglés y lectura interactiva de frases
python main.py -g gramaticas/1.txt                # conversión de expresiones y modo interactivo
python main.py -f "She eats a cake with a fork"   # validar una frase y terminar
python main.py -g gramaticas/1.txt -f "(id*id)+id"
python main.py -f "he cooks" --repeticiones 1000
python main.py -f "she eats pizza" --sin-pasos --sin-tabla --sin-imagen
python main.py -g gramaticas/anbn.txt -f "" --sin-imagen
python main.py -g gramaticas/ambigua.txt -f "id+id*id" --sin-imagen
python main.py -g gramaticas/1.txt --guardar-cnf salidas/1-cnf.txt
python main.py -f "The cat drinks the beer." --salida salidas/ejemplos
python main.py --help
```

El programa muestra cada paso de la simplificación (anulables, parejas unitarias, símbolos inútiles, variables nuevas) y el tiempo que tardó la conversión. Con `1.txt`, la CNF que se obtiene es idéntica a `1-cnf.txt`.

Sin `-f` pide frases hasta escribir `salir`, recibir fin de entrada o pulsar
Ctrl+C. La conversión se realiza una sola vez. `-f ""` analiza la cadena vacía.
`--sin-pasos` resume la conversión; `--sin-tabla` omite la tabla y `--sin-imagen`
omite la exportación de archivos del árbol. Por defecto se guardan en `salidas/`.

Fragmento de una salida real para el primer ejemplo (el tiempo varía por equipo):

```text
Frase: She eats a cake with a fork
Tokens (7): she | eats | a | cake | with | a | fork
Resultado: SÍ — la frase pertenece al lenguaje de la gramática.
Árboles de derivación: 1
Notación con corchetes:
[S [NP she] [VP [VP [V eats] [NP [Det a] [N cake]]] [PP [P with] [NP [Det a] [N fork]]]]]
```

Una frase rechazada también termina con código 0: el análisis fue válido.
Los errores de lectura/formato devuelven 1 y los argumentos inválidos, 2.
La aceptación es sintáctica, no semántica. El árbol y el conteo corresponden
a la CNF; las expresiones pueden mostrar variables auxiliares. La aceptación
de ε se conserva al convertir la gramática original, pero esa bandera no se
incluye en el archivo de CNF exportado.

## Pruebas

```bash
python -m unittest discover -s pruebas -t . -v
```

**140 pruebas** verifican los algoritmos, formatos, árboles, Graphviz y la consola.
Incluyen la conversión exacta `1.txt` → `1-cnf.txt`, 781 comparaciones entre las
dos gramáticas y contrastes independientes de 4206 expresiones y 9723 secuencias
de palabras, además de derivaciones aleatorias con semillas fijas.
La prueba de PNG se omite automáticamente si Graphviz no está instalado.

## Documentación

El diseño, la discusión y los ejemplos están en [`docs/reporte.md`](docs/reporte.md).

- [Diseño de la aplicación](docs/reporte.md#1-diseño-de-la-aplicación).
- [Discusión, obstáculos y recomendaciones](docs/reporte.md#2-discusión).
- [Ejemplos, tiempos, imágenes y pruebas](docs/reporte.md#3-ejemplos-y-pruebas-realizadas).

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
| `ambigua.txt` | Expresiones sin precedencia: `id+id*id` tiene dos árboles. |

## Estructura del proyecto

```text
proyecto2-ToC/
├── main.py                    # Consola, orquestación y medición de tiempos
├── algoritmos/                # Simplificación, CNF y CYK sin entrada/salida
├── modelos/                   # Gramatica y NodoArbol
├── entrada_salida/            # Archivos, tokenización, formatos y Graphviz
├── gramaticas/                # Nueve gramáticas de ejemplo
├── pruebas/                   # Suite unittest y contrastes independientes
├── docs/
│   ├── reporte.md             # Diseño, discusión y resultados
│   └── imagenes/              # Tres árboles PNG del reporte
├── salidas/                   # Archivos generados; ignorados por Git
└── README.md
```

## Graphviz (opcional, para la imagen del árbol)

En Windows se puede instalar con `winget install --id Graphviz.Graphviz -e`.
Verifica la instalación con `dot -V`. Si no se reconoce el comando, agrega
`C:\Program Files\Graphviz\bin` al PATH y abre otra terminal. El programa también
busca las rutas habituales de instalación de Windows.

Sin Graphviz el programa funciona igual y guarda el archivo `.dot`, que puede
abrirse en cualquier visor de DOT.
