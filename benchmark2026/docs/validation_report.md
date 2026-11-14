# Informe de validación (v0.2)

Fecha: 2026-11-14. Generador 0.2.0 (piloto v0.1 con `pilot_v01.py`), semilla 2026. Las cifras salen de las ejecuciones reales de `validate_dataset.py` (`results/validation_*.json`) y de `pytest`.

## 1. Resultado automático

| Conjunto | Archivo | Ítems | Familias | Errores | Advertencias |
|---|---|---:|---:|---:|---:|
| Benchmark v1 | `data/benchmark_v1.jsonl` (`51efbbfb…`) | 180 (60 A, 60 B, 60 C) | 73 | 0 | 0 |
| Piloto v0.1 | `data/pilot.jsonl` (`e1993e11…`) | 15 | 9 | 0 | 0 |
| Piloto de fracciones | `data/pilot_fractions.jsonl` (`8a6872bb…`) | 8 | 3 | 0 | 0 |
| Piloto de equivalencias | `data/pilot_equiv.jsonl` (`1f965621…`) | 8 | 3 | 0 | 0 |

El validador de v1 se ejecutó con `--expect-counts 60,60,60`, `--max-skill-share 0.12` y comprobó la ausencia de problemas repetidos frente a los pilotos.

**Pruebas (`pytest`): 145 superadas.** Se reparten así: núcleo, reglas de error, restricciones y verificadores; comprobación independiente (33 vectores a mano, 3 000 entradas aleatorias, 6 mutaciones); propiedades de los datasets (cantidades, familias, fugas, cero, restricciones oficiales frente a metodológicas, aislamiento de `FRAC-EQUIV` y `MUL-TENS`, regeneración exacta, otras semillas) y motor con un servidor Ollama falso.

## 2. Qué comprueba el validador por ítem

Esquema JSON; trazabilidad a la matriz (fila, páginas, extracto del indicador dentro de la fila, estado verificado); competencia habilitada en ese split; límites efectivos; respuesta recalculada con **tres implementaciones** (Python exacto, SymPy e `independent_check`); números y fracciones del enunciado frente a la spec; coherencia entre trabajo estudiantil y error; **comprobación independiente del error** (`docs/manual_verification.md`); fugas en la pista de referencia; duplicados y casi duplicados; coherencia de familias; fugas entre archivos; legibilidad (enunciado de 45 palabras como máximo); y que ningún ítem declare revisión docente.

## 3. Cobertura y distribución de v1

Detalle en `docs/coverage_report.md`.

- Dificultad propuesta: básica 64, intermedia 68, avanzada dentro del grado 48. Son etiquetas de diseño.
- 9 controles (trabajo correcto) entre los 60 ítems de diagnóstico.
- 94 ítems involucran el cero (ver `docs/zero_policy.md`).
- Mayor participación de una competencia: 8,9 %.
- Competencias con pocos ítems: `SUB-CHECK-REINTEGRATIVE` (2) y `DIV-CHECK-REINTEGRATIVE` (1). Solo admiten la tarea A.
- Sin ítems: `MUL-TENS` (pendiente de interpretación) y `FRAC-EQUIV` (solo piloto).

## 4. Ambigüedades registradas

- 33 ítems (15 de diagnóstico y 18 de pistas) tienen ambigüedad alta: el estudiante solo escribió el resultado, sin procedimiento. Se registran hipótesis y no se afirma una causa.
- Las pistas que mencionan "reagrupar" (resta con reagrupación) usan una estrategia que el programa no nombra explícitamente. La regla M-SUB-3 la permite; debe revisarse con docentes.
- En el piloto de equivalencias, el indicador oficial pide "argumentar"; la parte de argumento no se puntúa automáticamente.

## 5. Prueba del motor con un Ollama real

Se ejecutaron 4 ítems del piloto con `qwen3.5:2b` (Q8_0) en tu Ollama local (versión 0.40.16). Resultado: el motor registró el digest, la cuantización informada (coincide con la esperada), la versión, la carga en frío, los tokens, el tiempo hasta el primer token medido por el cliente y el estado de `ps` (incluido `size_vram` tal como lo informó Ollama). La puntuación automática funcionó. Fue una **prueba de funcionamiento**: no es un resultado del benchmark ni de Qwen3-0.6B. Ese modelo no estaba disponible en el servidor del puerto 11434.

## 6. Limitaciones

- Las tres implementaciones y los vectores a mano los escribió la misma persona (Claude): la independencia es de código, no de criterio. Falta que una persona repase los vectores y una muestra de ítems.
- No se valida la naturalidad del español, la pertinencia de los contextos ni la dificultad: eso exige revisión docente.
- El control de casi duplicados usa similitud de texto y números; no detecta duplicados semánticos.
- Los enunciados salen de plantillas: hay menos variedad que en un aula real.
- Ninguno de los 180 ítems ni de los pilotos fue revisado por docentes (`human_reviewed = false`).
- El motor no se probó con Qwen3-0.6B Q4_K_M ni sobre los 180 ítems.

## 7. Pendiente

1. Ejecutar Qwen3-0.6B Q4_K_M en la computadora del investigador.
2. Revisión docente de ítems, dificultad y rúbrica.
3. Estrato de cero y evaluación del indicador de equivalencia.
4. Aclarar el alcance de "decenas completas".
