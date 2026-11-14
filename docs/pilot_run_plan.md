# pilot_run_plan.md — Plan de la primera evaluación sobre `pilot` (registro previo)

**Fecha:** 2026-11-14 (≈ 01:27 UTC) · **Estado:** plan y huellas fijados **antes** de ejecutar. La sección «Resultado» se escribe después y no modifica lo de arriba.

## Qué es y qué no es
Primera evaluación de Qwen3-0.6B en tres precisiones sobre la partición `pilot` del dataset sintético (27 problemas base, 81 ítems). **Es exploratoria:** el dataset no tiene revisión docente, no hay rúbrica, y solo se puntúan métricas deterministas. No valida el currículo ni la calidad pedagógica, y no es evidencia sobre móviles.

## Qué queda congelado (huellas SHA-256)
| Elemento | Huella |
|---|---|
| Dataset `dataset/data/items.jsonl` | `49e0b23196045a6a99b856c591be272213655a1b01a906430ebbdc6f5c519f82` |
| Prompt `prompt-v0.5b` (plantillas + prompt de sistema) | `fc1af120764809200b53847ee0eafd837702a4c39bc4604fa7ab1648818a4b08` |
| Corrector `runner/src/score.py` | `8a21625f400cfa9f22bc38bc4a8c5a462efcc7c2fd4529d158c0d56aa68f6b10` |
| `runner/src/run_experiment.py` | `cb3cba1c8703c3eaef20a94e5cf9bec1ebbaf0aac1870e331b50cf954572dbe0` |
| `runner/src/run_matrix.py` | `765cd769b05cfa97d82de7c787c0d9eba62500f171f546ed42eec7dfa7fce14c` |
| Configuración `runner/configs/experiment.json` | `c389bfd5eb67b99b687a6a4abdde4bd9dd7173fac8a9e1c2b8ab1e85b89cc467` |

**Después de ver resultados no se cambia nada de lo anterior.** Si se halla un defecto en el corrector o el prompt, se reporta, se corrige como versión nueva y se informan **ambos** resultados.

## Diseño
- Modelos: `qwen3:0.6b-q4_K_M`, `qwen3:0.6b-q8_0`, `qwen3:0.6b-fp16` (digests verificados), siempre **en secuencia e intercalados** con rotación; nunca en paralelo.
- Ítems: partición `pilot` completa, las tres tareas (`solve`, `diagnose`, `hint`).
- 1 pase de calentamiento descartado y **3 repeticiones medidas** por modelo: 972 registros en total, 729 medidos.
- Parámetros: temperatura 0, semilla 42, contexto 2048, `num_predict` 256, `think:false`. Equipo conectado a corriente, GPU libre, solo local.
- Un solo llamado por (ítem, repetición); no se descartan ni se repiten respuestas por su contenido.

## Métricas (solo deterministas)
| Tarea | Métrica |
|---|---|
| `solve` | Exactitud de la respuesta final. Se reportan una **tasa estricta** (lo no legible cuenta como fallo) y una **tasa sobre lo legible**, con el número de «sin extracción» |
| `diagnose` | Acierto del veredicto «correcta/incorrecta»: **sensibilidad** (21 problemas con error) y **especificidad** (6 controles con respuesta correcta). No puntúa si localizó bien el error |
| `hint` | Ausencia de fuga del resultado correcto en la pista (por cociente en divisiones). No puntúa utilidad, claridad ni progresión |
| Repetibilidad | Ítems con respuesta idéntica en las 3 repeticiones; ítems cuya puntuación cambia |
| Costo (reportado por Ollama) | Mediana de tokens/s y de segundos por respuesta, por precisión, solo en pases medidos. **No son mediciones independientes de RAM, VRAM ni energía** |

## Análisis (descriptivo; sin p-values)
- **Unidad: el ítem** (promedio de sus 3 repeticiones). Los 3 ítems de un problema base no son independientes, así que los intervalos de confianza se calculan con **bootstrap por conglomerados (por problema base)**: 10 000 remuestreos, semilla 12345, percentiles 2,5–97,5.
- **Comparación entre precisiones, emparejada por ítem:** diferencia de medias (A − B) con su intervalo por conglomerados, y recuento de ítems a favor de A, a favor de B y empates.
- Con 27 problemas los intervalos serán anchos. **No se harán afirmaciones causales ni de «no hay diferencia»** (el intervalo ancho no demuestra ausencia de efecto). El método final de incertidumbre se decide con el mentor (D-03).

## Lo que NO se va a afirmar
- Calidad pedagógica de diagnósticos o pistas (no hay rúbrica ni revisión humana).
- Que el resultado generalice a otros modelos, otros problemas o dispositivos móviles.
- Que el prompt congelado sea óptimo: se ajustó por legibilidad con otro conjunto de problemas.
- Equivalencia con el currículo vigente.

## Limitaciones conocidas
Un solo modelo en tres precisiones; dataset sintético sin validar; formato de división que delata la operación (D-08, pendiente del mentor); el corrector no puede leer todas las respuestas (se reporta); tiempos reportados por Ollama, en un portátil.

## Resultado
Ejecutado el 2026-11-14 (01:25–01:31 UTC) según este plan, sin desviaciones en el diseño ni en lo congelado: las cinco huellas se verificaron **antes y después** y coinciden. 972 registros, 0 errores, 0 truncadas. Resultados, auditoría manual y límites en `pilot_results_qwen3_0.6b.md`.
Únicas notas: (a) se añadió al corrector, **antes** de fijar su huella, que guarde `eval_count` y duraciones para poder reportar velocidad (cambio aditivo); (b) el informe `pilot_report.py` se escribió durante la corrida siguiendo la sección «Análisis» de este plan, y falló al imprimir un carácter en la consola de Windows después de escribir sus archivos (corregido, solo presentación).
