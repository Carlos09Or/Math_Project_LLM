# Plan de rondas repetidas y ablación del diagnóstico (escrito antes de correr)

Fecha: 2026-11-14. Todo lo de abajo se fijó **antes** de ver los resultados de las rondas adicionales y de las ablaciones. Lo que se haga distinto se anota como desviación.

## 1. Por qué

La primera pasada fue una corrida por configuración. Falta saber (a) cuánto varía un resultado de una ronda a otra y (b) por qué los modelos dan por bueno un trabajo equivocado en la tarea B.

## 2. Rondas repetidas

| Conjunto | Config | Rondas | Semilla |
|---|---|---|---|
| Deterministas | `evaluation.yaml` congelada (temperatura 0, top_k 1) | `round2`, `round3` (la ronda 1 es la primera pasada) | 2026 |
| Con muestreo | `evaluation_sampling.yaml` (temperatura 0.7, top_p 0.8, top_k 20) | `s1`, `s2`, `s3` | 101, 102, 103 |

- Las 7 configuraciones se corren **intercaladas**: en cada ronda, todas, en un orden aleatorio propio de la ronda. Antes de cada modelo se descargan los que estén cargados, para que el estado de la GPU sea el mismo.
- Mismo dataset, prompt y verificadores congelados. Solo cambian los parámetros de generación del conjunto con muestreo, y eso queda en cada manifiesto.
- Con temperatura 0 esperamos resultados casi idénticos entre rondas; lo que se mide ahí es el no determinismo del motor. La variabilidad real de muestreo se mide con las rondas `s1` a `s3`.

**Reglas para comparar** (fijadas ahora):
1. Se reporta cada ronda por separado y la media y la desviación entre rondas.
2. Una diferencia entre dos configuraciones se considera clara solo si (a) supera dos veces la desviación entre rondas de ambas y (b) el intervalo de la diferencia, calculado con remuestreo por familia (73 familias), no incluye 0.
3. Las diferencias entre familias de modelos siguen siendo no causales.

## 3. Ablación del diagnóstico (solo tarea B, 60 ítems, config congelada)

Variantes en `configs/ablation_B.yaml`, además del prompt congelado (línea base):

| Variante | Qué cambia | Qué separa |
|---|---|---|
| `solve_first` | Le pide resolver el problema antes de opinar y luego comparar | ¿Falla por no resolver, o por no verificar? |
| `given_answer` | Le da la respuesta correcta y le pide compararla con la del estudiante | ¿Falla por no saber la respuesta, o por no comparar/inclinarse a «correcto»? |

**Hipótesis (antes de ver datos):**
- **H1, sesgo a decir «correcto».** Los modelos no fallan por no saber la respuesta. Predicción: con `given_answer` el acierto de veredicto sube mucho (al menos 80 % en la mayoría de configuraciones).
- **H2, brecha de verificación.** Dentro de una familia, los modelos resuelven bien el problema (tarea A) y aun así dan por bueno el trabajo equivocado (tarea B). Predicción: entre las familias en que el modelo acertó la tarea A, más de la mitad de los errores se dan por buenos.
- **H3, el procedimiento visible ayuda poco.** Los modelos no detectan mejor los errores aritméticamente falsos que están a la vista que los demás. Predicción: la tasa de detección con una igualdad falsa escrita es similar a la de los demás casos.

**Qué se concluye según el resultado:**
- Si H1 se cumple, el problema es de seguimiento de la tarea o de sesgo, no de capacidad matemática, y un componente determinista de comprobación resolvería la parte aritmética.
- Si `given_answer` no ayuda, el problema es de comparación o de seguir la instrucción, y habría que revisar el formato de la tarea.
- Si `solve_first` ayuda pero poco, resolver antes no basta para verificar.

## 4. Lo que no mide esto

- No valida la explicación del error ni la calidad pedagógica (sin revisión humana).
- Las variantes de prompt son exploratorias; no sustituyen al prompt congelado.
- Las rondas siguen siendo en un solo equipo, sin medición de memoria ni energía.
