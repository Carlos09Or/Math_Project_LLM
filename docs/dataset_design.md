# dataset_design.md — Estructura y trazabilidad curricular del benchmark

**Fecha:** 2026-11-13 · **Estado:** diseño propuesto; **nada aquí está validado por docentes**. Los ejemplos son sintéticos y demostrativos.

> **Actualización 2026-11-14:** el primer borrador de 90 ítems ya está generado y validado en `../dataset_v0.1/` (ver su `README.md`). Cambios respecto a este diseño: `competency_id` lleva sufijo de edición (`A3-SUB-24`); `rubric_version` es `rubric_v0.1_not_written` (la rúbrica no existe aún); se añadieron `operation`, `operands`, `gold_answer_struct` y `student_answer_struct` para verificación automática; la partición es `dev` (3 problemas) y `pilot` (27). Los problemas se redactaron con las dos propuestas de este diseño (edición 2024 y 6 controles con respuesta correcta), **pendientes de la decisión del mentor (D-04, D-06)**.

## 1. Principios
1. Primero se valida el *pipeline* con los 9 ítems sintéticos del starter; el benchmark curricular se amplía después (`roadmap.md`, F2).
2. **La unidad experimental es el problema base** (`problem_base_id`); los ítems de las tres tareas derivados del mismo problema no son independientes. Esto determina las particiones y el análisis estadístico.
3. **El error del estudiante se genera con una regla determinista conocida**, no se adivina. Así `gold_error_observable` es verdadero por construcción y el diagnóstico no inventa la intención del niño.
4. La corrección aritmética se verifica por cálculo (Python/SymPy), nunca solo con un LLM.
5. Problemas originales; no se copian ejercicios de textos protegidos. Cada ítem declara su procedencia.
6. Todo lo curricular queda `pending_validation` hasta que un docente o MEDUCA lo confirme.

## 2. Esquema de ítem

Se mantienen los 19 campos del protocolo v0.1 (nombres exactos) y se añaden los marcados con ★ para cerrar los hallazgos E-06 y E-07. `null` es válido donde se indica.

| Campo | Tipo | Oblig. | Reglas |
|---|---|---|---|
| `item_id` | string | sí | Único. Formato `{problem_base_id}-{S|D|H}` |
| `problem_base_id` | string | sí | Agrupa las tareas del mismo problema. Unidad de partición |
| `grade` | int | sí | `3` en el piloto |
| `locale` | string | sí | `es-PA` |
| `topic` | enum | sí | `sustraccion`, `multiplicacion`, `division` (propuesta; ver §4) |
| `competency_id` | string | sí | Referencia a `curriculum_map.csv` |
| `curriculum_doc` | string | sí | `M-2024` (referencia propuesta), `M-2014` o `M-2017` |
| `curriculum_version` | string | sí | Edición impresa del documento |
| `curriculum_page` | string | sí | Página impresa y página PDF |
| `task` | enum | sí | `solve`, `diagnose`, `hint` (`correct_step` y diálogo en F6) |
| `problem_text` | string | sí | Español con ortografía y tildes correctas |
| `student_answer` | string/null | según tarea | `null` en `solve` |
| `gold_answer` | string | sí | Calculado, no tecleado; se valida con código |
| `gold_error` | string/null | sí | Texto breve para el revisor; coincide con `gold_error_observable` |
| ★`gold_error_observable` | string/null | sí | Hecho verificable sobre la respuesta del estudiante («74 ≠ 84; las decenas son 7 en vez de 8»). `null` si la respuesta es correcta |
| ★`gold_error_type` | string/null | no | Etiqueta de una taxonomía revisada por docentes (§5); no se infiere una intención |
| ★`student_answer_is_correct` | bool/null | sí | Permite ítems de control sin error (E-07) |
| ★`error_generator` | string/null | sí | Regla determinista que produjo la respuesta errónea (p. ej., `sub_col_min_from_max`) |
| `difficulty` | enum | sí | `1`–`3`, definida por criterios objetivos (cifras, acarreos, residuo) |
| `provenance` | enum | sí | `synthetic_original`, `synthetic_demo`, `teacher_authored`, `adapted_from_X` |
| `reviewer_status` | enum | sí | `unreviewed`, `reviewed_1`, `reviewed_2`, `disputed` |
| `rubric_version` | string | sí | p. ej. `rubric_v0.1` |
| `split` | enum | sí | `dev`, `pilot`, y para adaptación futura `train`/`val`/`test`, asignado **por `problem_base_id`** |

Reglas del validador (a implementar en F1.5):
- `item_id` único; las tres tareas de un problema comparten `problem_base_id`.
- `gold_answer` se recalcula; si `student_answer_is_correct` es falso, `student_answer ≠ gold_answer`.
- Si hay `error_generator`, reproducir `student_answer` con esa regla.
- Ningún ítem `hint` puede contener `gold_answer` en el enunciado.
- Un `problem_base_id` no puede aparecer en dos `split`.

## 3. Trazabilidad curricular
El mapa (`curriculum_map.csv`) enlaza cada competencia con documento, página y rango numérico por edición.

Edición de referencia **propuesta: M-2024** (Programa de tercer grado 2024, aprobado en el marco del Decreto Ejecutivo 53/2024); M-2014 se conserva como edición histórica y M-2017 como referencia de «aprendizajes fundamentales». La decisión es del mentor (**D-04**). Rangos para 3.er grado: ver `sources_verification.md` §1.2.

Aviso: no se afirma que M-2024 sea el currículo vigente en 2026 (el Plan Estratégico 2025–2029 prevé una segunda versión actualizada); ver `sources_verification.md` §1.3.

## 4. Competencias candidatas para el piloto (a decidir con el mentor)

El prompt maestro pide dos o tres competencias observables. Propuesta:

| Código | Competencia (resumen de M-2024) | Páginas M-2024 (impresa) | Por qué es observable |
|---|---|---|---|
| `A3-SUB` | Sustracción de naturales con y sin reagrupación («pidiendo prestado») | 186–189 | Cada columna deja un error visible; la regla de error es determinista |
| `A3-MUL` | Multiplicación (tablas, algoritmo con llevadas, por decenas completas) | 188–191 | El olvido de la llevada o el desalineamiento de subproductos son verificables |
| `A3-DIV` | División exacta e inexacta con residuo (dividendos de hasta 3 cifras, divisores de 1–2 cifras) | 192–197 | Un residuo mayor o igual que el divisor es un error observable |

La adición (pp. 184–185) y los problemas verbales atraviesan las tres: cada problema base se redacta como situación cotidiana. Las fracciones (pp. 198 en adelante) quedan fuera del piloto.

**Rangos del piloto (propuesta conservadora):** números de hasta 4 cifras en sustracción y multiplicación (4 cifras × 1–2 dígitos), dividendos de hasta 3 cifras y divisores de 1–2 cifras. Se amplía solo tras validar la rúbrica (Pr §3).

## 5. Diseño del piloto: 30 problemas base × 3 tareas

Meta **provisional** (no es potencia estadística justificada; **D-03**).

| Dimensión | Propuesta |
|---|---|
| Problemas base | 30 = 3 competencias × 10 |
| Dificultad | 1/2/3 repartida de forma pareja dentro de cada competencia |
| Ítems | 30 `solve` + 30 `diagnose` + 30 `hint` = 90 |
| **Controles negativos** | De los 30 problemas, **6** (2 por competencia) llevan una respuesta del estudiante **correcta**. En `diagnose` el resultado esperado es «sin error». En `hint` el resultado esperado es una pista de verificación sin afirmar el resultado; si el mentor prefiere no usar `hint` en estos 6, quedan 84 ítems (**D-06**) |
| Taxonomía de errores | `A3-SUB`: restar el dígito menor del mayor en cada columna; no reducir el dígito prestado; omitir el préstamo en las decenas. `A3-MUL`: olvidar la llevada; error de tabla; desalinear subproductos; omitir el cero del subproducto. `A3-DIV`: residuo ≥ divisor; ignorar el residuo; omitir un cero en el cociente. **Hipótesis de taxonomía: validar con docentes** |
| Particiones | Por `problem_base_id`; no hay entrenamiento en esta fase. El campo existe para F8 |

## 6. Tres ejemplos demostrativos (sintéticos, **no son datos de evaluación**)

Cálculos verificados por script el 2026-11-13: 4305 − 1278 = 3027; resta columna a columna con el dígito menor del mayor da 3173; 12 × 7 = 84; 85 ÷ 4 = 21 con residuo 1.

```json
{"item_id":"DEMO-SUB-001-S","problem_base_id":"DEMO-SUB-001","grade":3,"locale":"es-PA","topic":"sustraccion","competency_id":"A3-SUB","curriculum_doc":"M-2024","curriculum_version":"Programa de tercer grado 2024","curriculum_page":"186-189 (PDF 188-191)","task":"solve","problem_text":"En una bodega había 4305 cajas de jugo. Se vendieron 1278 cajas. ¿Cuántas cajas quedan?","student_answer":null,"gold_answer":"3027","gold_error":null,"gold_error_observable":null,"gold_error_type":null,"student_answer_is_correct":null,"error_generator":null,"difficulty":2,"provenance":"synthetic_demo","reviewer_status":"unreviewed","rubric_version":"rubric_v0.1","split":"dev"}
{"item_id":"DEMO-MUL-001-D","problem_base_id":"DEMO-MUL-001","grade":3,"locale":"es-PA","topic":"multiplicacion","competency_id":"A3-MUL","curriculum_doc":"M-2024","curriculum_version":"Programa de tercer grado 2024","curriculum_page":"188-191 (PDF 190-193)","task":"diagnose","problem_text":"Una caja tiene 12 lápices. ¿Cuántos lápices hay en 7 cajas?","student_answer":"74","gold_answer":"84","gold_error":"El resultado es 74 y no 84: al hacer 7 × 2 = 14 se escribió el 4 y no se sumó el 1 que se lleva a las decenas.","gold_error_observable":"74 ≠ 84. En 7 × 12, el producto de las unidades es 14 (se escribe 4 y se lleva 1); las decenas quedaron en 7 (7 × 1) y no en 8.","gold_error_type":"omision_de_llevada","student_answer_is_correct":false,"error_generator":"mul_omit_carry","difficulty":1,"provenance":"synthetic_demo","reviewer_status":"unreviewed","rubric_version":"rubric_v0.1","split":"dev"}
{"item_id":"DEMO-DIV-001-H","problem_base_id":"DEMO-DIV-001","grade":3,"locale":"es-PA","topic":"division","competency_id":"A3-DIV","curriculum_doc":"M-2024","curriculum_version":"Programa de tercer grado 2024","curriculum_page":"192-197 (PDF 194-199)","task":"hint","problem_text":"Se reparten 85 caramelos entre 4 niños por igual. ¿Cuántos caramelos recibe cada niño y cuántos sobran?","student_answer":"Cada niño recibe 20 y sobran 5","gold_answer":"Cada niño recibe 21 y sobra 1","gold_error":"Sobran 5 caramelos y hay 4 niños: todavía se puede repartir uno más a cada niño.","gold_error_observable":"El residuo (5) es mayor o igual que el divisor (4): el reparto no ha terminado.","gold_error_type":"residuo_mayor_o_igual_que_divisor","student_answer_is_correct":false,"error_generator":"div_stop_early","difficulty":2,"provenance":"synthetic_demo","reviewer_status":"unreviewed","rubric_version":"rubric_v0.1","split":"dev"}
```

Las páginas M-2024 corresponden a las secciones del mapa; la página PDF = impresa + 2.

## 7. Rúbricas: criterios mínimos (el documento completo será `rubric_v0.1.md`)

Escala 0–2 por criterio, con ejemplos ancla por criterio y reporte por criterio (no solo un total):
- **Diagnóstico:** 0 = no localiza el error o inventa una causa; 1 = localiza el error pero con detalle incorrecto o impreciso; 2 = localiza el error observable de forma específica y correcta. Componente determinista: ¿declara que la respuesta es correcta/incorrecta de acuerdo con `student_answer_is_correct`?
- **Utilidad de la pista:** 0 = no ayuda o es incorrecta; 1 = relevante pero genérica; 2 = orienta al paso donde está el error y es progresiva.
- **Claridad apropiada a la edad:** 0 = vocabulario o estructura inadecuados; 1 = comprensible con esfuerzo; 2 = claro para 3.er grado.
- **No-revelación (penalización):** detección determinista de `gold_answer` en la pista, más revisión humana de la revelación implícita. Es una restricción de la pista, no una puntuación adicional.
- **Solve:** exactitud por cálculo; explicación revisada por humano (corrección y legibilidad).

## 8. Qué necesita revisión docente
1. Que los problemas base sean pertinentes y claros para 3.er grado.
2. Que los rangos numéricos y la edición curricular sean los que se aplican.
3. La taxonomía de errores (§5): ¿son errores reales y frecuentes?
4. Las rúbricas y los ejemplos ancla.
5. Una muestra de las respuestas del modelo, **sin saber qué modelo ni qué precisión**, con doble anotación de una submuestra; registro de acuerdos, desacuerdos e incertidumbre.
6. Perfil de docentes necesario (pregunta 3 del protocolo; **PENDIENTE** con el mentor).

## 9. Ética, licencias y contaminación
- **Datos:** solo ítems sintéticos; sin respuestas ni datos de menores. Cualquier recolección con niños requiere consentimiento, permisos y evaluación ética (fuera de alcance).
- **Licencias:** los ítems propios se licencian al publicarse (decisión pendiente). **No** se copian datos ni código de MathTutorBench (licencia sin resolver).
- **Contaminación:** los problemas son originales y se redactan sin consultar benchmarks públicos; los textos aritméticos simples pueden coincidir con datos de preentrenamiento. Se documentará: método de redacción, fecha y búsqueda de coincidencias en GSM8K y MathDial (**PENDIENTE**). No se afirma ausencia de contaminación.
- **Documentos MEDUCA:** se citan con página; no se reproducen ejercicios de los programas.
