# Dataset card: benchmark curricular de Matemática, 3.er grado (Panamá, MEDUCA 2026)

Versión: `benchmark_v1` (generador 0.2.0, semilla 2026, esquema 0.1, restricciones 0.3, prompts-v1.0). Estado: **borrador sin revisión docente**. Congelado el 2026-11-14 (`configs/freeze_v1.json`).

## 1. Finalidad

Medir, con los mismos ítems y las mismas condiciones, cómo cambian la exactitud matemática, la capacidad de identificar errores de un estudiante y la calidad de las pistas pedagógicas cuando distintos modelos de lenguaje pequeños se ejecutan bajo restricciones computacionales (por ejemplo, distintas cuantizaciones). Forma parte de la investigación "Resource-Efficient Offline AI Tutoring for Primary Education".

**Es un conjunto de evaluación.** No debe usarse para entrenar ni ajustar los modelos que luego se comparen.

## 2. Contenido

180 ítems: 60 de resolución de problemas (A), 60 de diagnóstico de errores (B) y 60 de generación de pistas (C), en 73 familias de problemas base. Idioma: español de Panamá. Área: Aritmética (19 competencias habilitadas; ver `docs/coverage_report.md`).

- **Dificultad propuesta**: 64 básicos, 68 intermedios, 48 avanzados dentro del grado. Son etiquetas de diseño, no medidas.
- **Controles**: 9 de los 60 ítems de diagnóstico muestran un trabajo correcto, para medir si el modelo inventa errores.
- **Cero**: 94 ítems involucran cero en cifras, operandos o respuestas (ver `docs/zero_policy.md`).

Cada ítem guarda: referencia curricular (fila de la matriz, páginas oficiales, extracto del indicador), los límites aplicados separados en documentados y metodológicos, el enunciado, el trabajo estudiantil (tareas B y C), la respuesta correcta con su `problem_spec` legible por máquina, el error registrado y su ambigüedad, y la rúbrica aplicable.

## 3. Fuentes

- Programa de Estudio de Tercer Grado, Matemáticas, Actualización 2026, Fase de Validación (MEDUCA), páginas impresas 181-228. SHA-256 del archivo consultado: `4ac0a6f91c6e757aa851ac62ca5d31f80aa8e1df4bead25ba0898fd5e30eea78`.
- Un compendio analítico previo, usado solo para planear el cotejo.
- MathTutorBench (Macina et al., EMNLP 2025) como referencia metodológica, leído de forma parcial. Lo que viene de allí y lo que es propuesta nuestra está separado en `docs/pedagogical_rubric.md`.

No se copian ejercicios del programa ni de guías. Los problemas se generan por código con plantillas originales. No se afirma que sean inéditos en el mundo; se aplican controles de similitud interna y contra los pilotos.

## 4. Metodología de construcción

Cada ítem nace de una `problem_spec` determinista. La respuesta se calcula con tres implementaciones independientes. Los errores del estudiante los produce una regla determinista y se comprueban con fórmulas independientes del generador (`docs/manual_verification.md`). El validador (`src/validate_dataset.py`) hace comprobaciones de esquema, trazabilidad, límites, exactitud, coherencia, fugas en las pistas, duplicados y familias. Resultado: 0 errores y 0 advertencias en los 180 ítems.

**Documentado frente a metodológico.** Cada límite numérico del benchmark lleva su origen en `curriculum/skill_constraints.json`. Los límites **oficiales** salen del programa (con página). Los **metodológicos** son decisiones nuestras y no deben presentarse como exigencias de MEDUCA. Por ejemplo: "divisor de una cifra" es oficial (p. 197); "todo resultado es menor que 10 000" y "denominadores de 2 a 10 en suma y resta de fracciones" son metodológicos.

## 5. Inclusión y exclusión

**Incluido**: competencias de Aritmética con contenido verificado en el PDF oficial y evaluación definida.

**Excluido**:
- `MUL-TENS` (multiplicación por decenas completas): el alcance no está claro en el programa.
- `FRAC-EQUIV`: piloto independiente de 8 ítems (`data/pilot_equiv.jsonl`, split `pilot_equiv`). No forma parte del benchmark principal hasta definir la evaluación del indicador "argumenta".
- Casos de actividades sugeridas que superan los límites (50 000, 12 345), multiplicación multidígito general, divisores de dos cifras distintos de 10, 100 y 1000, fracciones con denominadores distintos, dinero con decimales.
- Álgebra, Medidas, Geometría y Estadística (solo inventariadas).

## 6. Revisión

- **Automática**: superada (ver arriba).
- **Docente**: **ninguna**. Todos los ítems llevan `human_reviewed = false` y `status = draft`.
- **De MEDUCA**: ninguna. El benchmark no tiene validación oficial.

## 7. Evaluación y métricas

- Tarea A: exactitud con verificador determinista que separa respuesta incorrecta de error de formato.
- Tarea B: veredicto y categoría automáticos; descripción por revisión humana.
- Tarea C: detector de fugas automático; calidad pedagógica por rúbrica humana (`RUBRIC-PED-v0.1`, sin validar con docentes).
- La exactitud matemática y la calidad pedagógica se reportan por separado.

## 8. Límites y riesgos conocidos

- **Desequilibrio**: las competencias de operaciones pesan más (hasta 8,9 % cada una). `SUB-CHECK-REINTEGRATIVE` y `DIV-CHECK-REINTEGRATIVE` solo tienen 2 y 1 ítems de tarea A, porque no tienen un error estudiantil natural que simular.
- **Pocos ítems por competencia**: cualquier comparación por competencia es orientativa. Los ítems de una familia no son independientes.
- **Plantillas**: los enunciados salen de plantillas, así que el vocabulario y la estructura son menos variados que en el aula.
- **Sesgo de cuantización posible**: un modelo cuantizado puede fallar por el formato de respuesta y no por la matemática; se reporta el cumplimiento de formato aparte.
- **Etiquetas de error**: la taxonomía de errores es propuesta del benchmark. La tarea B ofrece una lista cerrada, lo que la convierte en clasificación con opciones.
- **Ambigüedad**: 33 ítems (15 de diagnóstico y 18 de pistas) registran ambigüedad alta, porque el estudiante solo escribió el resultado. No se atribuyen razonamientos que no se vean.
- **Categorías desiguales**: de los 111 trabajos con error, 39 son errores de procedimiento, 23 de concepto, 17 de valor posicional, 14 de confusión de operación, 9 de cálculo y 9 de interpretación del problema. Los errores de cálculo y de interpretación tienen pocos casos.
- **Cero**: cobertura limitada del cero como valor (ver `docs/zero_policy.md`).
- **Semilla**: no garantiza determinismo de la ejecución de los modelos.

## 9. Licencia y uso

No se ha fijado una licencia para este conjunto. Debe decidirla el investigador. El programa de MEDUCA es un documento oficial citado por referencia, sin reproducir sus textos. Si se publica el benchmark, hay que revisar las condiciones de uso del PDF oficial y las licencias de las referencias metodológicas (la licencia de MathTutorBench aparece de forma contradictoria entre CC BY y CC BY-SA en sus páginas).

## 10. Usos no recomendados

- Entrenar o ajustar modelos con estos ítems.
- Presentar los resultados como una medición de aprendizaje de niños reales.
- Presentarlo como validado por MEDUCA o por docentes.
- Concluir sobre la calidad pedagógica sin la revisión humana con rúbrica.
- Usar las etiquetas de dificultad como si fueran empíricas.
- Mezclarlo con el dataset anterior basado en el programa 2024.
