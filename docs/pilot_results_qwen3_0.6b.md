# pilot_results_qwen3_0.6b.md — Primera evaluación sobre `pilot`: Qwen3-0.6B en tres precisiones

**Fecha:** 2026-11-14 · **Estado:** exploratorio, según `pilot_run_plan.md` (plan y huellas fijados antes de correr).
**Qué es y qué no es:** descripción de lo que hicieron tres precisiones del mismo modelo sobre un dataset **sintético sin revisión docente**, con métricas **solo deterministas**. **No** mide calidad pedagógica, **no** valida el currículo y **no** generaliza a otros modelos ni a dispositivos móviles.

## Ejecución
| Elemento | Valor |
|---|---|
| Matriz | `20261114T012526Z_9a95b4`, 01:25:25 → 01:31:52 UTC (6 min 27 s) |
| Diseño | 3 precisiones × 81 ítems × (1 calentamiento + 3 repeticiones), **en secuencia e intercaladas**, orden rotado; GPU pura; equipo conectado a corriente |
| Registros | 972 (729 medidos, 243 de calentamiento); **0 errores, 0 truncadas** |
| Modelos (digest) | `q4_K_M` `7df6b6e09427…`, `q8_0` `f6358994266d…`, `fp16` `626c9556a80f…` |
| Prompt | `prompt-v0.5b` congelado; huellas de dataset, prompt, corrector, runner y configuración **verificadas antes y después**: coinciden con el plan |
| Formato legible | `solve`: 237 de 243 respuestas leídas de la línea `Respuesta final:` (97,5 %); el resto, por el respaldo; **ninguna quedó sin leer**. `diagnose`: 100 % con línea `Veredicto:` |

Los registros crudos están en `runner/runs_pilot/` (excluida de git: los manifiestos tienen rutas locales). La única incidencia fue de presentación: el informe falló al imprimir un carácter en la consola de Windows, después de escribir sus archivos (corregido).

## Resultados por precisión
Tasa por ítem (promedio de sus 3 repeticiones); IC 95 % por *bootstrap* por problema base (10 000 remuestreos, semilla 12345). «Estricta» cuenta lo no legible como fallo (aquí no hubo).

| Tarea y métrica | Ítems | fp16 | q4_K_M | q8_0 |
|---|---|---|---|---|
| **solve**, exactitud | 27 | 70,4 % [51,9–85,2] | 59,3 % [40,7–77,8] | 70,4 % [51,9–85,2] |
| **diagnose**, sensibilidad (ítems con error) | 21 | 42,9 % [23,8–61,9] | 57,1 % [38,1–76,2] | 57,1 % [38,1–76,2] |
| **diagnose**, especificidad (controles) | 6 | 83,3 % [50,0–100] | 50,0 % [16,7–83,3] | 50,0 % [16,7–83,3] |
| **hint**, sin fuga del resultado | 27 | 59,3 % [40,7–77,8] | 25,9 % [11,1–44,4] | 51,9 % [33,3–70,4] |

### Diferencias emparejadas por ítem (A − B, puntos porcentuales)
| Tarea | A − B | Diferencia | IC 95 % | Ítems a favor de A / de B / empates |
|---|---|---|---|---|
| solve | q4_K_M − q8_0 | −11,1 | [−25,9; 0,0] | 0 / 3 / 24 |
| solve | q4_K_M − fp16 | −11,1 | [−25,9; 0,0] | 0 / 3 / 24 |
| solve | q8_0 − fp16 | 0,0 | [0,0; 0,0] | 0 / 0 / 27 |
| diagnose (error) | q4_K_M − fp16 | +14,3 | [0,0; +28,6] | 3 / 0 / 18 |
| diagnose (control) | q4_K_M − fp16 | −33,3 | [−66,7; 0,0] | 0 / 2 / 4 |
| hint | q4_K_M − q8_0 | −25,9 | [−44,4; −7,4] | 1 / 8 / 18 |
| hint | q4_K_M − fp16 | −33,3 | [−55,6; −11,1] | 2 / 11 / 14 |
| hint | q8_0 − fp16 | −7,4 | [−22,2; +7,4] | 1 / 3 / 23 |

## Auditoría manual del corrector (contra las respuestas crudas)
- **solve:** los 3 ítems donde `q4_K_M` falla y `fp16` acierta son errores reales de cálculo: `PB-SUB-05` (1627 en vez de 1617), `PB-DIV-03` (residuo 7 en vez de 2) y `PB-DIV-09` (cociente 738 en vez de 49).
- **hint:** las fugas detectadas son reales (p. ej., «50/5 = 10», «158/7 = 22»).
- **diagnose:** todos los veredictos se leyeron de una línea `Veredicto:`.

## Lectura con cuidado
**Resolver.** `q8_0` y `fp16` aciertan **los mismos 27 ítems**; `q4_K_M` falla 3 ítems más. El IC de la diferencia llega justo a 0: con 27 problemas no se puede distinguir de «sin diferencia» ni de una caída moderada. Es una señal compatible con la hipótesis H1 (la cuantización agresiva puede costar exactitud), **no una prueba**.

**Diagnosticar.** Las tres precisiones están **cerca del azar**. En la primera repetición, los veredictos correctos fueron 15 de 27 (`q4_K_M` y `q8_0`) y 14 de 27 (`fp16`). La mayor especificidad de `fp16` no indica que distinga mejor: dice «correcta» más a menudo en general (17 de 27 veces frente a 12 de `q4_K_M`), lo que sube la especificidad y baja la sensibilidad a la vez. Con solo 6 controles esa cifra es muy inestable (IC 50–100 %). Por la composición del dataset (21 de 27 tienen error), responder siempre «incorrecta» acertaría 21 de 27: por eso se reportan sensibilidad y especificidad por separado y ninguna sola cifra resume el diagnóstico.

**Pistas.** Es donde las precisiones **más se separan**, y los intervalos de `q4_K_M` frente a las otras dos no cruzan 0. En la primera repetición, `q4_K_M` incluyó el resultado en 20 de 27 pistas, `q8_0` en 13 y `fp16` en 11. La causa visible: `q4_K_M` tiende a resolver paso a paso (89 tokens de media frente a 29–40), y esos pasos contienen el resultado. Dos advertencias: (1) «sin fuga» **no** significa «pista buena»: `fp16` respondió, por ejemplo, «La respuesta correcta sería: 45…» dando por buena la respuesta errónea del estudiante, algo que este corrector no detecta; (2) en los 6 controles casi toda pista cuenta como fuga **por definición** (repetir la respuesta correcta que el estudiante ya tiene); en los 21 ítems con error, las fugas fueron 14 (`q4_K_M`), 7 (`q8_0`) y 6 (`fp16`).

**Repetibilidad.** Respuesta idéntica en las 3 repeticiones: `fp16` 81 de 81 ítems, `q8_0` 78 de 81, `q4_K_M` 76 de 81. **Ningún ítem cambió de puntuación** entre repeticiones.

**Costo (reportado por Ollama, no medido de forma independiente).** Mediana de tokens/s: `q4_K_M` 218, `q8_0` 211, `fp16` 131. Mediana de segundos por respuesta: 0,37, 0,27 y 0,44. El tiempo por respuesta depende de cuánto escribe cada modelo (p. ej. `q4_K_M` escribió pistas más largas), por lo que **no equivale a la velocidad por token**. No hay medición de RAM, VRAM ni energía.

## Lo que NO se concluye
- Que una precisión sea «mejor» pedagógicamente: no hay rúbrica ni revisión humana; las métricas son solo exactitud, veredicto y fuga.
- Que estas diferencias existan fuera de este dataset sintético de 27 problemas: los intervalos son anchos y varios llegan a 0.
- Que el efecto sea causal o generalice a otras familias de modelos: es un solo modelo en tres precisiones.
- Nada sobre dispositivos móviles: el laboratorio es un portátil con GPU NVIDIA.

## Limitaciones
Dataset sintético sin validación docente; prompt ajustado por legibilidad con otro conjunto de problemas; formato de división que delata la operación (D-08, pendiente del mentor); solo 6 controles; corrector determinista que no evalúa calidad pedagógica ni detecta que una pista dé por buena una respuesta errónea; tiempos de un portátil, reportados por Ollama.

## Siguiente
1. **Rúbrica y revisión humana** (ciega) de una muestra de diagnósticos y pistas: sin ellas, «sin fuga» y «veredicto» son indicadores toscos.
2. Decisiones del mentor (D-03 incertidumbre, D-08 formatos, D-04 currículo).
3. Más problemas, y más controles para especificidad, antes de afirmar diferencias entre precisiones.
4. Instrumentación de costo real (VRAM, RAM, energía, TTFT) en la fase 4.
