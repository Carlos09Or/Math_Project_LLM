# prompt_tuning_dev.md — Ajuste del formato del prompt (registro previo)

**Fecha:** 2026-11-14 · **Estado:** criterios fijados **antes** de ejecutar las variantes. La sección «Resultado» se rellena después y no modifica lo de arriba.

## Para qué es esto
En la corrida exploratoria sobre `dev`, fp16 y q8 escribieron la línea final de las divisiones como `Respuesta final: 21 <87>, 0`, que el corrector no puede leer. Si el formato no se lee, el corrector no puede puntuar `solve`. Se ajusta **cómo se pide el formato**, no lo que se evalúa.

## Reglas para no sobreajustar
1. **Se ajusta solo el formato de salida de `solve`** (la frase final que pide `Respuesta final: …`). Los prompts de `diagnose` y de `hint` **no se tocan**.
2. **Se elige por legibilidad del formato, NO por exactitud.** La exactitud no entra en la decisión.
3. **Se prueba con un conjunto aparte**, `dataset/data/format_probes.jsonl` (SHA-256 `05be3bdd27d501b52b9071b9c5b7d74fcc26eea05aad53be7a14f8510546981e`): 12 problemas nuevos (4 por operación) cuyos operandos y enunciados no coinciden con ninguno del dataset de evaluación (lo comprueba una prueba automática). No son datos de evaluación y no se reportan como resultados. Con ello no se mira `pilot` ni se ajusta a los 3 problemas de `dev`.
4. **Una vez elegida la variante, se congela.** Si después de ver resultados de `pilot` se cambia, es una versión nueva y se reportan ambas.

## Variantes (difieren solo en la última frase de `solve`)
| Versión | Cómo pide el formato (sub / mul) | Cómo pide el formato (división) |
|---|---|---|
| `prompt-v0.3` (línea base) | `Respuesta final: <número>` | `Respuesta final: cociente <número>, residuo <número>` |
| `prompt-v0.4a` | `Respuesta final: N` + «reemplaza N por el número» | `… cociente N, residuo M` + «sin símbolos < >» |
| `prompt-v0.4b` | formato del ejemplo con otro número: `Respuesta final: 123` | ejemplo con otros números: `… cociente 7, residuo 2` |
| `prompt-v0.4c` | «empiece con "Respuesta final:" seguida solo del resultado» | «… diga el cociente y el residuo con esas palabras» |

Los ejemplos de `v0.4b` (123; 7 y 2) no coinciden con ninguna respuesta correcta de las sondas.

## Diseño de la prueba
- Modelos: las tres precisiones de Qwen3-0.6B (`q4_K_M`, `q8_0`, `fp16`), en secuencia e intercalados (nunca en paralelo).
- Solo la tarea `solve`; 1 pase de calentamiento descartado y 2 repeticiones medidas.
- Unidades por variante: 12 problemas × 3 precisiones × 2 repeticiones = **72 registros**, de los cuales 24 son divisiones.
- Mismos parámetros que el resto (temperatura 0, semilla 42, contexto 2048, `num_predict` 256, `think:false`).

## Regla de decisión
- **Métrica principal:** tasa de formato = proporción de registros de `solve` cuya respuesta se leyó de la línea `Respuesta final:` (método `final_line`), agrupando las tres precisiones.
- **Se elige la variante con la mayor tasa de formato**, siempre que cumpla **a la vez**: tasa global ≥ 90 % y tasa en divisiones ≥ 80 %.
- **Empate:** si dos variantes difieren en 3 puntos porcentuales o menos, gana la de instrucción más corta.
- **Si ninguna cumple los umbrales:** no se congela ninguna; se informa y se decide con el mentor cómo proceder (p. ej., aceptar «sin extracción» como parte de lo que se mide).
- Se reporta también la exactitud, **después** de decidir y solo a título informativo.

## Limitaciones declaradas
- 12 problemas y un solo modelo: la variante elegida puede no servir con otras familias; en la fase de más modelos hay que repetir esta comprobación de formato.
- Los modelos añaden restos como `/no_think`; no se corrigen aquí.
- Esto ajusta la **legibilidad**, no la calidad pedagógica.

## Resultado (rellenado después de ejecutar; lo de arriba no se modificó)

### Incidencia de ejecución
En la primera tanda solo corrieron `prompt-v0.3` y `prompt-v0.4a`: `prompt-v0.4b` y `prompt-v0.4c` se abortaron porque `run_matrix.py` comprobaba la GPU justo después de descargar los modelos, antes de que la memoria se liberara (defecto corregido, con prueba de regresión). Las dos variantes se reejecutaron después, con la misma configuración y **sin que se hubiera visto ni puntuado ningún resultado de ninguna variante**. Los registros están en `runner/runs_dev/` (excluida de git: los manifiestos tienen rutas locales).

### Tasa de formato (72 registros por variante; 24 son divisiones)
| Variante | Formato global | Formato en divisiones | Sin extracción | Por precisión (fp16 / q4_K_M / q8_0) |
|---|---|---|---|---|
| `prompt-v0.3` | 72,2 % | 16,7 % | 20 | 67 % / 83 % / 67 % |
| `prompt-v0.4a` | **88,9 %** | **83,3 %** | 2 | 92 % / 75 % / 100 % |
| `prompt-v0.4b` | 77,8 % | 33,3 % | 16 | 75 % / 83 % / 75 % |
| `prompt-v0.4c` | 69,4 % | 8,3 % | 6 | 67 % / 75 % / 67 % |

### Decisión según la regla escrita antes
**Ninguna variante cumple los umbrales** (global ≥ 90 % **y** divisiones ≥ 80 %). `prompt-v0.4a` es claramente la mejor y cumple en divisiones, pero queda en 64/72 = 88,9 % frente al 90 % requerido (le faltó **un registro**). Por la regla: **no se congela ninguna** y se decide con el mentor cómo proceder. El umbral no se relaja a posteriori.

### Qué falló en `prompt-v0.4a` (8 de 72 registros)
- El modelo **copia la instrucción literalmente** como línea final (`Respuesta final: N (reemplaza N por el número).`) o escribe `Respuesta final: 24, 0.` sin las palabras «cociente» y «residuo».
- Los 8 fallos son de solo **3 problemas distintos** (`PRB-MUL-03`, `PRB-DIV-01`, `PRB-DIV-03`), idénticos entre repeticiones, y casi todos de `q4_K_M` (6) y `fp16` (2). Con 12 problemas, el 90 % depende de muy pocos ítems.
- **Limitación del corrector:** cuando el modelo copia la plantilla, el respaldo extrajo un número equivocado del texto (el `7` de «7 días») y puntuó 0. Quedan marcados como `fallback` (cuentan solo en la tasa «sin extracción»/estricta), pero el respaldo no es fiable en ese caso.

### Sobre la exactitud informativa (no usada para decidir)
La exactitud aparente fue 54 % (v0.3), **86 % (v0.4a)**, 53 % (v0.4b) y 81 % (v0.4c). La diferencia entre variantes se debe sobre todo a que lo no legible cuenta como fallo, no a que el modelo calcule mejor: **el formato afecta lo que se mide**, razón por la que debe fijarse antes de evaluar.

### Opciones (decisión pendiente del investigador y del mentor)
1. **Segunda ronda con registro previo nuevo**, con variantes que eviten que el modelo copie la instrucción, probadas en un **conjunto de sondas nuevo** (estas 12 ya se vieron, así que usarlas otra vez las sobreajustaría). Mismos umbrales.
2. **Aceptar `prompt-v0.4a` tal cual** declarando que quedó a un registro del umbral y que el resto se cuenta como fallo de formato («estricta»). Es la opción más rápida y la que más se aparta de la regla.
3. **Llevarlo al mentor** antes de decidir.
