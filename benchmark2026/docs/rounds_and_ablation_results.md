# Rondas repetidas y ablación del diagnóstico: resultados (exploratorios)

Fecha: 2026-11-14. Plan: `rounds_and_ablation_plan.md`, escrito antes de ver estos datos. Datos: `results/analysis_rounds.json` y `results/analysis_diagnosis_round1.json`. 49 corridas, todas sin errores de ejecución. Una sola máquina, sin revisión humana ni docente.

## 1. Variabilidad entre rondas

Rondas deterministas: la ronda 1 (primera pasada) más `round2` y `round3`. Rondas con muestreo (temperatura 0.7, top_p 0.8, top_k 20): `s1`, `s2`, `s3`, con semillas 101, 102 y 103.

**Con temperatura 0 casi no hay variación.** En seis de las siete configuraciones las respuestas fueron idénticas en las tres rondas, ítem por ítem. En Qwen3-0.6B Q4_K_M cambió una respuesta de 180. Eso indica que repetir con la configuración congelada aporta poco.

**Con muestreo la resolución sí varía**, y mucho en algunos modelos (aciertos de 60 en cada ronda):

| Configuración | Ronda 1 (temp. 0) | s1 | s2 | s3 | Media ± sd (muestreo) |
|---|---:|---:|---:|---:|---|
| Qwen3-0.6B Q4_K_M | 39 | 40 | 31 | 35 | 35,3 ± 4,5 |
| Qwen3-0.6B Q8_0 | 36 | 37 | 37 | 36 | 36,7 ± 0,6 |
| Qwen3-0.6B FP16 | 37 | 37 | 37 | 35 | 36,3 ± 1,2 |
| Qwen3-1.7B Q4_K_M | 55 | 53 | 54 | 52 | 53,0 ± 1,0 |
| Gemma 3 1B Q4_K_M | 25 | 22 | 24 | 22 | 22,7 ± 1,2 |
| SmolLM3 3B Q4_K_M | 51 | 51 | 54 | 51 | 52,0 ± 1,7 |
| Phi-4-mini 3.8B Q4_K_M | 49 | 51 | 53 | 45 | 49,7 ± 4,2 |

- Una diferencia de 3 a 4 aciertos entre dos configuraciones, como Q4 frente a Q8 en el 0.6B, **cae dentro del ruido**. La primera pasada de 39 de 60 para Q4_K_M era, en media con muestreo, 35.
- Los modelos pequeños son menos consistentes. En los problemas del Qwen3-0.6B Q4_K_M, con muestreo, 23 se aciertan siempre, 26 a veces y 11 nunca. En Qwen3-1.7B son 47, 10 y 3.
- El **veredicto de diagnóstico es muy estable incluso con muestreo** (casi idéntico en las tres rondas): el sesgo a decir «correcto» no es ruido.
- Las pistas que revelan la respuesta sí varían con muestreo (por ejemplo, Phi-4-mini 12, 7 y 10 de 60).

## 2. Comparaciones con intervalos por familia

Se usa la regla del plan: diferencia clara solo si supera 2 desviaciones entre rondas y el intervalo, por remuestreo de las 73 familias, no incluye 0. Con desviación 0 en el diagnóstico, la regla se apoya solo en el intervalo.

| Comparación | Resolución (de 60) | Diagnóstico, veredicto (de 60) |
|---|---|---|
| Qwen3-1.7B frente a 0.6B Q4_K_M | **+17**, clara | **+16**, clara |
| 0.6B Q4_K_M frente a Q8_0 | +2 (det.) / −1 (muestreo), no clara | **−6**, clara |
| 0.6B Q4_K_M frente a FP16 | +1 / −1, no clara | **−6**, clara |
| 0.6B Q8_0 frente a FP16 | −1 / 0, no clara | 0 (idénticos) |
| Phi-4-mini frente a SmolLM3 | −2, no clara | +6, no clara |
| Phi-4-mini frente a Qwen3-1.7B | −6 / −3, no clara | **+15**, clara |
| SmolLM3 frente a Qwen3-1.7B | −4 / −1, no clara | **+9**, clara |

- **Resolución:** el tamaño dentro de la familia Qwen3 es una diferencia clara. La cuantización del 0.6B no lo es, y entre Qwen3-1.7B, SmolLM3 y Phi-4-mini no hay diferencia clara.
- **Diagnóstico:** aparece algo nuevo. **Q4_K_M detecta menos errores que Q8_0 y FP16** (3 de 51 frente a 9 de 51, estable en las 3 rondas deterministas y en las 3 de muestreo) aunque resuelve igual de bien. Q8_0 y FP16 son idénticos. Es una diferencia pequeña en valores absolutos, pero consistente. Es coherente con la idea de que la cuantización daña primero las tareas más difíciles, y no se puede afirmar que sea causal fuera de esta familia.
- **Diagnóstico entre familias:** Phi-4-mini y SmolLM3 diagnostican claramente mejor que Qwen3-1.7B, aunque este último resuelve mejor o igual.

## 3. Ablación del diagnóstico (60 ítems, config congelada)

Errores detectados de 51 (controles aceptados, de 9, entre paréntesis; errores de formato solo si afectan):

| Configuración | Línea base | `solve_first` | `given_answer` |
|---|---:|---:|---:|
| Qwen3-0.6B Q4_K_M | 3 (9) | 0 (9) | 2 (9) |
| Qwen3-0.6B Q8_0 | 9 (9) | 4 (9) | 15 (9) |
| Qwen3-0.6B FP16 | 9 (9) | 4 (9) | 18 (9) |
| Qwen3-1.7B Q4_K_M | 19 (9) | **40** (9) | **45** (9) |
| Gemma 3 1B | 3 (9) | 10 (8) | 11 (4), 18 errores de formato |
| SmolLM3 3B | 30 (7) | 40 (8) | **48** (9) |
| Phi-4-mini 3.8B | 34 (9) | 34 (8) | **47** (7) |

### Contra lo que predije
- **H1** (con la respuesta dada, el acierto sube a 80 % o más en la mayoría): **solo se cumple en 3 de 7** (Qwen3-1.7B 45/51, SmolLM3 48/51, Phi-4-mini 47/51). En los tres modelos de 0.6B y en Gemma **no**: aun con la respuesta correcta delante, apenas la comparan. Para los modelos de 1.7B o más, fallar es un problema de verificar, no de saber la respuesta. Para los más pequeños, es de comparar o de seguir la instrucción.
- **H2** (aceptan el trabajo erróneo aunque resolvieron el problema): se cumple en los modelos pequeños. En Qwen3-0.6B Q4_K_M, 31 de 32 casos; en Gemma, 20 de 21; en Qwen3-1.7B, 30 de 47. No se cumple en SmolLM3 (16 de 44) ni en Phi-4-mini (13 de 45).
- **H3** (una igualdad falsa a la vista no ayuda a detectarla): se cumple. Detectan con una igualdad falsa escrita casi igual que sin ella (Phi-4-mini: 14 de 25 frente a 20 de 26).

### Otros hallazgos
- **Resolver antes de opinar ayuda a unos y perjudica a otros:** sube mucho a Qwen3-1.7B (19 a 40) y a SmolLM3 (30 a 40), no cambia a Phi-4-mini y **empeora a los 0.6B** (3 a 0, 9 a 4, 9 a 4).
- **Dar la respuesta correcta no arregla la categoría.** Con `given_answer` el mejor resultado en veredicto y categoría a la vez es 12 de 51 (Qwen3-1.7B y Phi-4-mini).
- **Falsas alarmas:** con `given_answer`, Phi-4-mini aceptó solo 7 de los 9 trabajos correctos (marcó error en 2). Gemma aceptó 4 de 9 y tuvo 18 errores de formato, así que esa fila no es interpretable.

## 4. Qué se concluye
1. Los modelos de 1.7B o más **sí saben comparar** cuando se les da la respuesta. Su problema en el diagnóstico es no verificar por iniciativa propia. Un componente determinista que calcule la respuesta correcta y se la dé al modelo recupera la mayor parte de la capacidad de detección (45 a 48 de 51).
2. Los modelos de 0.6B y Gemma 3 1B **no sirven como jueces** del trabajo de un niño, ni siquiera con la respuesta a la vista.
3. La cuantización a 4 bits no se notó en resolver, pero sí en detectar errores del Qwen3-0.6B (menos aciertos que Q8_0 y FP16, de forma consistente).
4. Con muestreo, resultados de 3 o 4 aciertos de diferencia no se pueden distinguir del ruido en los modelos pequeños.

## 5. Límites
- Una sola máquina, sin revisión humana de las explicaciones. La categoría del error es nuestra propuesta.
- Las variantes del prompt son exploratorias. El prompt congelado y el benchmark no cambiaron.
- La desviación entre rondas con tres rondas es una estimación débil.
- Los resultados entre familias de modelos no son causales.
