# Metodología (v0.2)

## 1. Procedencia curricular

- El insumo inicial fue un compendio parafraseado (estados O y T). Se cotejó después con el PDF oficial del programa (SHA-256 en `skill_constraints.json`); el resultado está en `curricular_audit.md`.
- Estados de la matriz: `verificado_pdf_oficial_texto_y_visual` (Aritmética, con revisión visual de las tablas) y `verificado_pdf_oficial_solo_pagina_y_tema` (otras áreas). Ninguno implica aval de MEDUCA.
- El benchmark principal usa solo Aritmética. Las otras áreas están inventariadas.
- La edición de referencia es **MEDUCA 2026**. No se mezclan resultados ni datos con el dataset anterior, basado en el programa 2024.

## 2. Tres clases de restricción

`skill_constraints.json` separa de forma estricta:

| Clase | Significado | Dónde se ve |
|---|---|---|
| **Oficial verificada** | Enunciado del programa, con página y ubicación | `documented`, y `origin: documented` en los límites efectivos |
| **Metodológica propuesta** | Decisión del equipo (con id `M-*` y justificación) | `methodological`, y `origin: methodological` |
| **Pendiente de interpretación** | El alcance no está claro en la fuente oficial | `classification.pending_interpretation` (`MUL-TENS`) |

Además, `classification.pilot_only` agrupa lo que está verificado pero sin evaluación definida (`FRAC-EQUIV`). Cada ítem guarda `limits_applied` con los dos tipos de límite por separado.

Ejemplos de la separación: "divisor de una cifra" y "denominador hasta 10 al comparar fracciones" son **oficiales**. "Todo resultado de operación es menor que 10 000", "denominadores de 2 a 10 en suma y resta de fracciones" y "el resultado es una fracción propia" son **metodológicos**. El `FRAC-ADDSUB-HOMOG` se habilitó con decisión del investigador del 2026-11-14 y sus límites numéricos están marcados como metodológicos.

## 3. Verificación matemática

- Cada ítem lleva una `problem_spec` legible por máquina. La respuesta se recalcula con tres implementaciones: Python exacto (`math_core`), SymPy con otros algoritmos y un módulo independiente (`independent_check`). Si difieren, el ítem se rechaza.
- Ningún modelo de lenguaje decide si una operación es correcta.
- El verificador de respuestas normaliza separadores de miles, unidades, números en palabras, ordinales, fracciones y sí/no. Separa `incorrect` de `format_error` y deja casos ambiguos en `needs_manual_review`.
- La comprobación de errores estudiantiles es independiente del código que los genera (`manual_verification.md`).

## 4. Errores estudiantiles

Las categorías (`calculation_error`, `operation_confusion`, `place_value_error`, `procedural_error`, `problem_misinterpretation`, `concept_error`) son una propuesta del benchmark, no de MEDUCA. Cada error nace de una regla determinista visible en lo que el estudiante escribió. Si hay varias causas plausibles, se registran como hipótesis con ambigüedad alta y no se afirma una causa.

## 5. Familias, fugas y duplicados

- Una familia es un problema base. Sus variantes (resolver, diagnosticar, pista) comparten identificador, spec y enunciado. Una familia nunca debe repartirse entre entrenamiento y prueba.
- El validador rechaza familias repartidas en splits, specs repetidas, enunciados idénticos, casi duplicados (misma plantilla y casi los mismos números) y problemas que ya existan en los pilotos.
- Los problemas son originales de esta investigación. No se afirma que sean inéditos en el mundo.

## 6. Distribución y cobertura

La cuota por competencia y tarea está en `generate_dataset.QUOTAS`. Es proporcional al peso de cada competencia en el programa (las operaciones pesan más), no idéntica. `docs/coverage_report.md` documenta cobertura, desequilibrios y ausencias. Las competencias que no admiten un error estudiantil natural (`SUB-CHECK-REINTEGRATIVE`, `DIV-CHECK-REINTEGRATIVE`) solo aparecen en la tarea A.

## 7. Congelación y reproducibilidad

- `src/freeze.py` guarda el SHA-256 del dataset, los pilotos, la matriz, las restricciones, el esquema, los prompts, la configuración, los verificadores y el generador. `run_benchmark.py` se niega a evaluar si algo cambió (salvo `--allow-unfrozen`, que queda registrado en el manifiesto de la corrida).
- Cada familia usa un RNG derivado de (semilla, clave de familia, intento). Cada ítem guarda versión del generador, semilla y plantilla. No hay marcas de tiempo en los datos.
- La semilla no garantiza determinismo de la ejecución de los modelos entre motores, versiones o configuraciones.

## 8. Motor de evaluación

- Prompts uniformes por tarea (`configs/prompts.yaml`), idénticos para todos los modelos. No incluyen la respuesta, el error esperado ni la pista de referencia.
- Registro por respuesta: modelo, prompt exacto y su hash, parámetros efectivos, respuesta completa y visible, puntuación automática, métricas de inferencia y estado de la revisión pedagógica (`pending`).
- Registro por corrida: digest del modelo, cuantización informada por Ollama frente a la esperada, versión de Ollama, hashes del dataset y de la configuración.
- Solo se guardan cifras que informa Ollama (`/api/chat`, `/api/ps`) o el reloj del cliente. **No se miden ni se estiman** memoria, GPU ni energía. `ps_after_run` copia lo que Ollama informa de memoria de vídeo, si lo informa.

## 9. Evaluación

- Tarea A: exactitud automática.
- Tarea B: veredicto y categoría automáticos; descripción por revisión humana.
- Tarea C: detección automática de fugas; calidad por revisión humana (`pedagogical_rubric.md`).
- Los intervalos de Wilson del resumen son orientativos: hay pocos ítems por competencia y los ítems de una familia no son independientes.

## 10. Pendiente

- Revisión docente de ítems y rúbrica; calibración de dificultad.
- Estrato de cero (`zero_policy.md`).
- Definir la evaluación del indicador de equivalencia antes de incorporar `FRAC-EQUIV`.
- Aclarar el alcance de "decenas completas" (`MUL-TENS`).
- Ejecutar los modelos en la computadora del investigador.
