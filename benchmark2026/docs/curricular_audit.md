# Auditoría curricular: Matemática 3.er grado, MEDUCA 2026 (v0.2)

Fecha: 2026-11-14. Esta versión sustituye a la v0.1, que se apoyaba solo en el compendio.

## 1. Fuente cotejada

- Archivo: `prog-tercer_grado-2026.pdf` (374 páginas, SHA-256 `4ac0a6f9…eea78`). Lo proporcionó el investigador.
- La sección de Matemática ocupa las páginas impresas 181-228. La página impresa N está en la página N+1 del archivo. La bibliografía empieza en la 229.
- Aritmética (pp. 187-202): texto extraído y revisión visual de las tablas, para asignar cada viñeta a su columna.
- Álgebra, Medidas, Geometría y Estadística (pp. 203-228): solo texto extraído, suficiente para confirmar tema y página. No se recotejaron indicadores uno a uno.
- Este trabajo no cuenta con aval de MEDUCA ni revisión docente.

## 2. Qué cambió respecto al compendio

| Tema | Compendio (v0.1) | PDF oficial |
|---|---|---|
| Aritmética, números a división | O 188-197 | Confirmado: 188-197 |
| Ordinales | O 198-199 | Confirmado: 198-199, hasta 50° |
| Fracciones propias e impropias (4.1) | O 199 | Confirmado: p. 199 |
| Orden entre fracciones (4.2) | T 199-200 | Oficial, p. 200, con "denominadores naturales hasta 10" |
| Suma y resta de fracciones (4.3) | T 200 | Oficial, p. 201 |
| Equivalencia de fracciones (4.4) | T 200-201 | Oficial, pp. 201-202 |
| Álgebra | T 201-203 | Oficial, pp. 203-204 |
| Medidas | T 203-212 | Oficial, pp. 205-214 |
| Geometría | T 212-221 | Oficial, pp. 214-223 |
| Estadística | T 221-227 | Oficial, pp. 224-228 |

Consecuencias:

- **Fracciones**: las cuatro filas existen en el programa oficial. El límite de denominadores hasta 10 está documentado solo en 4.2 (p. 200). Los apartados 4.1, 4.3 y 4.4 no traen límite numérico.
- **División entre 10, 100 y 1000**: el programa incluye divisiones exactas **e inexactas** (p. 197). En la v0.1 yo había puesto "solo exactas"; ahora eso queda como no aplicable y se documenta la realidad.
- **Divisor de una cifra**: confirmado en el indicador de la página 197.
- **Operaciones combinadas**: el indicador de la página 197 incluye "problemas que requieren operaciones combinadas". El compendio no lo recogía. Permite ítems de dificultad intermedia y avanzada.
- **Objetivo de grado 4** (p. 187) menciona fracciones equivalentes como medio de comprobación. Mi afirmación de la v0.1 de que ningún objetivo las mencionaba era errónea.
- **Conteo por intervalos mayores que 2 (1 000 en 1 000)**, p. 190: nueva competencia `NAT-SKIP-COUNT`.
- **Propiedad reintegrativa de la división** (p. 197): nueva competencia `DIV-CHECK-REINTEGRATIVE`.

## 3. Discrepancias y ambigüedades

| ID | Hallazgo | Estado tras el cotejo |
|---|---|---|
| DISC-01 | Encabezado desplazado en las tablas del compendio | Era un defecto del compendio. La tabla oficial tiene 5 columnas (conceptual, procedimental, actitudinal, indicador, actividades). Cerrada |
| DISC-02 | Actividad de adición con 50 000 | Confirmada en el PDF oficial (p. 193) como actividad sugerida. Excluida |
| DISC-03 | Reparto de 12 345 juguetes | Confirmada (p. 197) como actividad sugerida. Excluida |
| DISC-04 | Divisor de una cifra | Confirmado como indicador (p. 197). Cerrada |
| DISC-05 | Adición: "hasta 10 000" frente a "hasta cuatro cifras" | Persiste. Restricción metodológica: suma <= 9 999 |
| DISC-06 | Sustracción sin mención de reagrupación | Persiste. Se permite y se documenta como decisión |
| DISC-07 | "Decenas completas" sin acotar el otro factor | Persiste. `MUL-TENS` pendiente |
| DISC-08 | Fracciones solo en transcripción | Resuelta: son oficiales. Persiste la falta de límites en 4.1, 4.3 y 4.4 |
| DISC-09 | Paginación T desplazada | Resuelta con la tabla de la §2 |
| DISC-10 | Temas sin objetivo de grado explícito | Corregida: el objetivo 4 sí menciona equivalentes. Siguen sin objetivo de grado explícito los ordinales y perímetro/área |
| DISC-11 | El compendio es una paráfrasis | Superada: la matriz cita ahora las páginas oficiales. El texto de la matriz sigue siendo paráfrasis cercana, no cita literal |
| DISC-12 | "Menores de 10 000" frente a "hasta 10 000" | Confirmada en el oficial. Regla M-GLOBAL-1 |
| DISC-13 | Páginas de Estadística inferidas | Resuelta con la §2 |
| DISC-14 | Objetivo de grado 2 sin límite numérico | Confirmada. El objetivo de área (p. 188) dice "menores de 10 000" |
| DISC-15 | Sin mapeo a objetivos generales de asignatura | Persiste: el programa no lo da. Columna `no_mapeado_en_programa` |
| DISC-16 | Los objetivos de Estadística mencionan pictogramas pero no hay tema de pictogramas | Nueva |
| DISC-17 | 4.2: el contenido dice "denominadores hasta 10" sin igualdad; el indicador exige igual denominador | Nueva. Se toma lo más estricto |
| DISC-18 | 4.4: el procedimental dice "comparación de fracciones" | Nueva |
| DISC-19 | El texto de "solución de problemas que requieren la multiplicación…" queda incompleto en el original (pp. 196-197) | Nueva |
| DISC-20 | En la fila de multiplicación aparece una actividad con divisiones exactas e inexactas (p. 196) | Nueva: desajuste de filas del original |
| DISC-21 | Dinero con decimales en Medidas (p. 207) | Nueva. Fuera de v1 |
| DISC-22 | El indicador de longitud menciona km; los contenidos no | Nueva. Fuera de v1 |

## 4. Competencias habilitadas para v1

Origen de los límites: **D** = documentado en el programa; **M** = decisión metodológica nuestra. El detalle está en `curriculum/skill_constraints.json`, que separa ambos tipos.

| skill_id | Estado | Límites efectivos principales |
|---|---|---|
| NAT-READ-WRITE | Habilitada | 1..10 000 (D hasta 10 000; M sin 0) |
| NAT-SKIP-COUNT | Habilitada | pasos 3, 4, 5, 10, 100, 1 000 (M); dentro de 10 000 (D) |
| NAT-ORDER-COMPARE | Habilitada | hasta 10 000 (D), máximo 3 números (M) |
| NAT-PLACE-VALUE | Habilitada | menores de 10 000 (D) |
| ADD-4DIG, ADD-PROPERTIES | Habilitada | sumandos de hasta 4 cifras (D); suma <= 9 999 (M); 2-3 sumandos (M) |
| SUB-10K, SUB-CHECK-REINTEGRATIVE | Habilitada | minuendo <= 9 999 (M; D dice hasta 10 000); reagrupación permitida (M) |
| MUL-TABLES-1-12 | Habilitada | factores 2..12 (D hasta 12; M excluye 1) |
| MUL-POW10 | Habilitada | x10, x100, x1000 (D); producto <= 9 999 (M) |
| DIV-EXACT, DIV-INEXACT | Habilitada | divisor 2..9 (D una cifra; M excluye 1); dividendo <= 9 999 (M) |
| DIV-POW10 | Habilitada | divisor 10/100/1000, exacta o inexacta (D); dividendo <= 9 999 (M) |
| DIV-CHECK-REINTEGRATIVE | Habilitada | dividendo = divisor x cociente + residuo (M: interpretación) |
| COMBINED-OPS | Habilitada | 2-3 pasos (M), cada paso dentro de su competencia |
| ORD-1-50 | Habilitada | 1.º a 50.º (D) |
| FRAC-REPR-CLASSIFY | Habilitada | denominador 2..10 (M), sin mixtos (M) |
| FRAC-COMPARE-HOMOG | Habilitada | igual denominador (D), denominador <= 10 (D) |
| MUL-TENS | **Pendiente de interpretación** (v0.3) | Alcance de "decenas completas" no claro en el oficial (DISC-07) |
| FRAC-ADDSUB-HOMOG | Habilitada el 2026-11-14 (v0.3) | Denominador 2-10 y resultado propio son M; "homogéneas" es D |
| FRAC-EQUIV | **Solo piloto independiente** (v0.3) | Sin límites documentados; todo límite es M |

Nota (histórica, v0.2) sobre las fracciones: pediste mantenerlas fuera hasta el cotejo. Tras el cotejo, `FRAC-REPR-CLASSIFY` y `FRAC-COMPARE-HOMOG` quedan habilitadas porque el programa documenta su contenido y, en la comparación, el límite de denominador. `FRAC-ADDSUB-HOMOG` y `FRAC-EQUIV` siguen fuera de la generación hasta que confirmes las restricciones, porque todo límite numérico sería nuestro. Si prefieres mantener las cuatro fuera, es un cambio de una línea en el JSON.

## 5. Áreas solo inventariadas

Álgebra, Sistema de Medidas, Geometría y Estadística y Probabilidad quedan en la matriz con página oficial y tema, sin generar ítems.

## 6. Límites de esta auditoría

- Los textos de la matriz son paráfrasis cercanas, no citas literales. La redacción exacta está en la página citada.
- La asignación de viñetas a la columna de indicador o de actividad se revisó visualmente solo en Aritmética.
- No se compararon versiones: si MEDUCA publica otra versión del programa, hay que repetir el cotejo.
- Relación con el trabajo anterior: el dataset v0.1 del proyecto usa el programa 2024 y no se tocó.

## 7. Decisiones del investigador (2026-11-14) y cambios de la v0.3

Se aplicaron sobre la matriz y `skill_constraints.json` (versión 0.3). Distinción estricta entre tres clases:

| Clase | Competencias |
|---|---|
| **Habilitadas** (contenido oficial; límites oficiales y metodológicos separados) | Todas las del §4 más `FRAC-ADDSUB-HOMOG` |
| **Solo piloto independiente** (verificada, evaluación sin definir) | `FRAC-EQUIV` |
| **Pendiente de interpretación** (alcance no claro en la fuente oficial) | `MUL-TENS` |

- **`FRAC-REPR-CLASSIFY` y `FRAC-COMPARE-HOMOG`**: se mantienen habilitadas. En la comparación, el límite "denominadores hasta 10" y la igualdad de denominador son oficiales (p. 200). En la clasificación, el límite 2-10 es metodológico.
- **`FRAC-ADDSUB-HOMOG`**: habilitada por decisión del investigador. El programa documenta solo "fracciones homogéneas" (p. 201). El límite de denominador 2-10 **no es oficial para este tema**: el "hasta 10" documentado es el de la comparación (4.2). También son metodológicos: operandos propios, resultado propio y positivo, sin mixtos, y la aceptación de formas equivalentes (M-FR3-1 a M-FR3-3).
- **`FRAC-EQUIV`**: piloto independiente (`data/pilot_equiv.jsonl`, 8 ítems). Se limita a lo que aparece en el objetivo de grado 4 (equivalencia como comprobación) y al indicador (p. 201): comprobar si dos fracciones son equivalentes y completar el numerador que falta. El argumento libre queda para revisión humana. No entra al benchmark principal.
- **`MUL-TENS`**: sigue fuera. Se releyeron las páginas 195-197: "multiplicación por decenas completas" aparece solo como enunciado, sin ejemplo ni indicador propio, y no aclara el otro factor ni si implica multiplicación multidígito. Pendiente de interpretación (DISC-07).
- **Cero**: `M-GLOBAL-3` se sustituyó por `M-ZERO-1`, que declara la exclusión de operandos iguales a 0 como comodidad temporal y no curricular. Ver `zero_policy.md`.
- **Dataset de 2024**: no se modificó ni se mezcló. La edición de referencia es 2026.
