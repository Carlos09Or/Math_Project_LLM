# prompt_tuning_dev_r2.md — Ajuste del formato del prompt, ronda 2 (registro previo)

**Fecha:** 2026-11-14 (≈ 01:15 UTC) · **Estado:** criterios fijados **antes** de ejecutar las variantes. La sección «Resultado» se rellena después y no modifica lo de arriba.
Continúa de `prompt_tuning_dev.md` (ronda 1), donde ninguna variante cumplió los umbrales.

## Qué enseñó la ronda 1 (y en qué se basan las variantes nuevas)
`prompt-v0.4a` fue la mejor (88,9 % de formato global, 83,3 % en divisiones; umbral 90 %/80 %). Sus fallos fueron: (a) el modelo **copiaba la indicación** como línea final (`Respuesta final: N (reemplaza N por el número).`) y (b) a veces escribía `Respuesta final: 24, 0.` sin las palabras «cociente» y «residuo». Se concentraron en 3 de 12 problemas.

## Reglas (iguales a la ronda 1; no se relajan)
1. Se ajusta **solo el formato de salida de `solve`**. Los prompts de `diagnose` y `hint` no se tocan (verificado por una prueba automática).
2. Se elige por **legibilidad del formato, no por exactitud**.
3. **Sondas nuevas:** `dataset/data/format_probes_r2.jsonl` (SHA-256 `5dfa4bebaa03ff4a77670db8cfdf019b46d5261eceac5df785e6945abe81fde6`), 12 problemas (4 por operación) cuyos operandos y enunciados **no coinciden** con los del dataset real ni con los de las sondas de la ronda 1 (lo comprueba una prueba). La ronda 1 ya se vio; reutilizarla sobreajustaría.
4. Los números de la respuesta de los ejemplos (`v0.5a`: valor 15; cociente 7, residuo 6) no coinciden, **por rol**, con ninguna respuesta del dataset ni de las sondas (prueba automática; una versión previa del ejemplo coincidía con un residuo de las sondas y se cambió antes de ejecutar).
5. Una vez elegida la variante, se **congela**. Cambiarla después de ver `pilot` es una versión nueva y se reportan ambas.

## Variantes (solo difieren en cómo se pide la línea final de `solve`)
| Versión | Qué cambia |
|---|---|
| `prompt-v0.4a` (línea base de la ronda 1, se vuelve a medir en las sondas nuevas) | `Respuesta final: N` / `cociente N, residuo M`, con «reemplaza N… sin símbolos < >» al final del enunciado |
| `prompt-v0.5a` | **Ejemplo resuelto completo** de otro problema antes del problema real (`Respuesta final: 15`; en divisiones `cociente 7, residuo 6`) y luego «termina con una última línea de la forma «Respuesta final: …» como en el ejemplo» |
| `prompt-v0.5b` | La **indicación de formato va ANTES del problema**, sin marcadores ni ejemplo («Escribe al final una línea que empiece con «Respuesta final:» seguida solo del número»; en divisiones, «…y diga el cociente y el residuo con esas palabras») |
| `prompt-v0.5c` | `v0.4a` + «No copies esta indicación.» |

## Diseño de la prueba
Igual que la ronda 1: las tres precisiones de Qwen3-0.6B (`q4_K_M`, `q8_0`, `fp16`), en secuencia e intercaladas (nunca en paralelo), solo `solve`, 1 pase de calentamiento descartado y 2 repeticiones medidas, mismos parámetros (temperatura 0, semilla 42, contexto 2048, `num_predict` 256, `think:false`). **72 registros por variante, 24 de ellos divisiones.**

## Regla de decisión (igual que la ronda 1)
- **Métrica principal:** tasa de formato = registros de `solve` cuya respuesta se leyó de la línea `Respuesta final:` (método `final_line`), agrupando las tres precisiones.
- **Se elige la variante con mayor tasa de formato**, siempre que cumpla **a la vez**: global ≥ 90 % y divisiones ≥ 80 %.
- **Empate:** si difieren 3 puntos porcentuales o menos, gana la de **instrucción más corta**.
- La exactitud se reporta **después** de decidir y solo de forma informativa.

## Esta es la última ronda
**Si ninguna variante cumple los umbrales, no se congela ninguna y NO habrá una ronda 3 sin decisión explícita del investigador y del mentor.** No se ajustan los umbrales ni la métrica después de ver los resultados.

## Limitaciones conocidas
- Un solo modelo (Qwen3-0.6B) y 12 problemas: la variante elegida puede no servir con otras familias; habrá que repetir la comprobación de formato en la fase de más modelos.
- **El formato de división delata la operación:** pedir «cociente y residuo» le dice al modelo que es una división. Afecta a todas las variantes por igual y es inherente a pedir ese formato; queda anotado como decisión de diseño (D-08).
- El respaldo del corrector (cuando falta la línea final) puede extraer un número equivocado si el modelo copia la plantilla; **no afecta a la decisión**, que usa solo `final_line`.
- Esto ajusta la **legibilidad**, no la calidad pedagógica.

## Resultado (rellenado después de ejecutar; lo de arriba no se modificó)

Ejecución sin incidencias: 4 matrices, 24 pasadas, 0 errores, 0 truncadas, GPU pura, siempre en secuencia. Registros en `runner/runs_dev_r2/` (excluida de git por las rutas locales de los manifiestos).

| Variante | Formato global (≥ 90 %) | Divisiones (≥ 80 %) | Sin extracción | Por precisión (fp16 / q4_K_M / q8_0) |
|---|---|---|---|---|
| `prompt-v0.4a` (línea base) | 83,3 % | 83,3 % | 4 | 83 % / 75 % / 92 % |
| `prompt-v0.5a` (ejemplo resuelto) | 80,6 % | 41,7 % | 2 | 83 % / 83 % / 75 % |
| **`prompt-v0.5b`** (formato antes del problema) | **97,2 %** | **91,7 %** | **0** | 100 % / 92 % / 100 % |
| `prompt-v0.5c` (+ «no copies») | 84,7 % | 83,3 % | 4 | 83 % / 83 % / 88 % |

### Decisión según la regla escrita antes
**`prompt-v0.5b` cumple los dos umbrales y es la única que los cumple** (por tanto no hizo falta el desempate). Se congela.

### Qué se congela
- `prompt-v0.5b` para `solve`; los prompts de `diagnose` y `hint` son los de `prompt-v0.3`, que **nunca se ajustaron**.
- Huella (SHA-256 de las plantillas de las cinco combinaciones tarea/operación más el prompt de sistema): `fc1af120764809200b53847ee0eafd837702a4c39bc4604fa7ab1648818a4b08`. Una prueba automática falla si cambia.
- `run_matrix.py` usa este prompt por defecto, y su partición por defecto sigue siendo `dev`: evaluar en `pilot` hay que pedirlo explícitamente.

### Cosas que conviene tener claras (no cambian la decisión)
- **Exactitud informativa** (no usada para decidir): v0.4a 68,1 %, v0.5a 76,4 %, **v0.5b 66,7 %**, v0.5c 70,8 %. El elegido tiene la exactitud aparente más baja de las cuatro, pero las diferencias son pequeñas, salen de 12 problemas y la métrica cuenta de forma distinta lo que se pudo leer (en v0.5b se leyó todo). La regla elegía por legibilidad, y eso se respeta; que el formato afecta a la exactitud medida es una propiedad conocida del método y por eso se fija antes de evaluar.
- **Una sola familia y 12 problemas:** la elección no está probada para otros modelos; al añadir familias hay que repetir la comprobación de formato.
- **Se ajustó con dos rondas** (la primera sin ganador). Se reportan ambas.
- El formato de división delata la operación (decisión de diseño D-08 anotada arriba).
- Pendiente del mentor: ratificar D-08 (formatos de salida del prompt) antes de evaluar en `pilot`.
