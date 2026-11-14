# experimental_protocol_v0.2.md — Protocolo experimental corregido

**Fecha:** 2026-11-13 · **Sustituye a:** Protocolo base v0.1 (13-nov-2026) y a `docs/protocol.md` del starter.
**Estado:** propuesto. **No sustituye la aprobación del mentor** ni la confirmación del currículo ni la revisión pedagógica. No hay resultados experimentales.
**Cómo leerlo:** cada cambio respecto a v0.1 se clasifica como **[E]** error objetivo, **[M]** mejora recomendada o **[D]** decisión pendiente del mentor (códigos de `audit.md`).

## 1. Qué cambia respecto a v0.1

| # | Cambio | Tipo | Motivo |
|---|---|---|---|
| 1 | Una sola versión de protocolo; el `protocol.md` del starter queda obsoleto | E-10 | Dos protocolos con diferencias de tamaño de muestra, campos y nombres |
| 2 | Se restituyen al plan de investigación multi-turno, paso correctivo, TTFT, energía y térmico, con fase de entrada (§3) | — | Estaban en P0 y no en v0.1; **no se retira nada del alcance de P0** |
| 3 | Las tres precisiones usan etiquetas, digests completos y tamaños verificados (§4) | — | Cierra «tags verificados» de v0.1 |
| 4 | Edición curricular de referencia propuesta: M-2024; M-2014 y M-2017 como históricas | D-04 | Existe una edición 2024 posterior |
| 5 | Repeticiones con calentamiento y orden intercalado | E-01, M-09 | `repeat_count` no se usaba; laptop con riesgo de *throttling* |
| 6 | Manifiesto de corrida y registro ampliado (§6) | E-03 | Faltaban datos para reproducir y auditar |
| 7 | Hoja de revisión ciega y clave separada | E-04 | La hoja revelaba el modelo y omitía el enunciado |
| 8 | Controles negativos y error generado por regla | E-06, E-07 | Verdad de referencia ambigua; sin medición de falsos positivos |
| 9 | Parámetros de muestreo completos y registrados | M-01 | `top_k/top_p/repeat_penalty` heredados sin registrar |
| 10 | Criterios de aceptación explícitos para cada hito (§9) | — | Distinguir «corrió» de «es evidencia» |

## 2. Pregunta, hipótesis y alcance

**Pregunta de P0 (largo plazo):** ¿cuál es la configuración mínima modelo–hardware–sistema que ofrece tutoría matemática offline pedagógicamente útil para primaria en dispositivos móviles de recursos limitados?

**Pregunta operativa de la fase de laboratorio:** ¿cómo cambian la exactitud, el diagnóstico de errores y la utilidad de las pistas, en aritmética de 3.er grado, cuando se cuantiza el mismo Qwen3-0.6B desde FP16 a Q8_0 y Q4_K_M, y qué recursos de inferencia se ahorran en un entorno local controlado?

**Hipótesis exploratorias** (por comprobar, no hallazgos):
- **H1.** La cuantización reduce memoria y almacenamiento, pero puede degradar las tareas pedagógicas de forma distinta a la exactitud de cálculo.
- **H2.** Diagnóstico y pistas pueden degradarse antes o de forma distinta que la resolución directa.
- **H3.** No hay una única configuración óptima; se estudia la frontera calidad–costo.
- **H4 (P0, etapa posterior).** El umbral de calidad depende de la tarea y se degrada con la dificultad y la longitud del diálogo (multi-turno).

**Dentro del primer experimento:** Qwen3-0.6B, tres precisiones, `solve`/`diagnose`/`hint`, PC local (laboratorio).
**Fuera del primer experimento, conservado en el plan:** ver §3. **Excluido en esta etapa:** aplicación o interfaz, datos de menores, entrenamiento.

## 3. Alcance de P0 conservado y su fase de entrada

| Elemento de P0 | Cómo se medirá | Fase | Limitación conocida |
|---|---|---|---|
| Consistencia multi-turno / degradación por longitud de diálogo | Diálogos de 2–5 turnos con el mismo problema base; registro por turno; métrica de coherencia con rúbrica | F6 | Requiere esquema de diálogo y revisión humana adicional |
| Paso correctivo siguiente | Tarea `correct_step`: el modelo propone el siguiente paso correcto; revisión con rúbrica y verificación determinista del paso | F6 | Definición operativa pendiente (D-07) |
| TTFT | *Streaming* de la API (tiempo hasta el primer fragmento) y, en F4, `llama-bench` | F4 | Ollama no lo entrega en modo no *streaming*; el tiempo hasta el primer fragmento incluye carga del modelo si no está caliente |
| RAM pico / VRAM | Muestreo del proceso de Ollama (RAM) y de `nvidia-smi` y `/api/ps` (VRAM, `size_vram` frente a `size`) | F3/F4 | La carga híbrida CPU/GPU se registra y se reporta por separado |
| Energía | Potencia de GPU muestreada con `nvidia-smi` (solo GPU, rotulada así); consumo total del equipo solo con instrumento externo (pendiente) | F4 | El portátil no permite medir el consumo del sistema completo sin hardware adicional |
| Comportamiento térmico | Temperatura de GPU y razones de reducción de frecuencia (`nvidia-smi`) durante corridas sostenidas | F4 | Un portátil introduce *throttling*; no es extrapolable a un teléfono |
| Pareto calidad–costo | Tablas y gráficos con *pandas* y *matplotlib* | F3 | Con 3 puntos del mismo modelo es una frontera descriptiva |
| Varias familias de modelos | Registro con cuantización explícita; comparación declarada como **no causal** | F5 | Distintas arquitecturas y datos de entrenamiento |
| LoRA/QLoRA y comparación de tres vías | Condicional a que la línea base muestre pérdida pedagógica | F8 | No se entrena en esta fase |
| Android / hardware con restricciones | Perfiles de dispositivos o emulación con RAM y cómputo limitados | F7 | **El laboratorio en PC no valida móvil** |

## 4. Modelo y configuración

### 4.1 Etiquetas (verificadas en `registry.ollama.ai`, 2026-11-13)

| Etiqueta | Digest completo del manifiesto | Peso (bytes) |
|---|---|---|
| `qwen3:0.6b-q4_K_M` | `7df6b6e09427a769808717c0a93cadc4ae99ed4eb8bf5ca557c90846becea435` | 522 640 096 |
| `qwen3:0.6b-q8_0` | `f6358994266d548dc070c564d49588fa3a6fac0cccd196bef38128aaa6ed22f3` | 832 278 240 |
| `qwen3:0.6b-fp16` | `626c9556a80fcb9c30ebd28292edf465ccda990282c5fb1e680d106d23bacc1c` | 1 509 347 040 |

Los tres comparten plantilla, licencia (Apache-2.0) y bloque de parámetros. Tras cada `pull` se debe comprobar que el digest local coincida; si no coincide, la corrida es inválida.

**Cabe en 6 GB de VRAM (estimación, NO verificada):** los pesos de FP16 (1,5 GB) son menores que 6 GB, pero no se afirma que la ejecución completa quepa en GPU sin comprobarlo con `ollama ps` (columna de procesador / `size_vram`) durante la corrida.

### 4.2 Parámetros de inferencia (todos fijos y registrados)

| Parámetro | Valor propuesto | Origen / nota |
|---|---|---|
| `temperature` | 0 | Starter. **D-01**: la ficha de Qwen3 recomienda 0.7 sin razonamiento y advierte contra la decodificación voraz en modo con razonamiento |
| `seed` | 42 | Starter; con T=0 es redundante pero se registra |
| `top_k`, `top_p`, `min_p`, `repeat_penalty` | Registrar los valores efectivos (etiqueta: 20, 0.95, `repeat_penalty` 1) | M-01 |
| `num_ctx` | 2048 | Starter; comprobar que ningún prompt se trunca (`prompt_eval_count`) |
| `num_predict` | 256 | Starter; **revisar tras el smoke test**: marcar y excluir/analizar respuestas con `done_reason ≠ stop` (M-02) |
| Política de *thinking* | `think:false` | Starter; **D-02**; verificar en la prueba que `thinking` está vacío y no aparece `<think>` en la respuesta |
| `keep_alive` | `5m` | Starter; se descarta una pasada de calentamiento antes de medir tiempos |
| Backend | Ollama 0.40.16 (`runner: llamacpp` según `/api/ps`) | Verificado; registrar versión en cada corrida |
| Prompt de sistema | Solo rol pedagógico; sin metainstrucciones de investigación | E-09; versionar (`prompt_version`) |

**Sensibilidad (propuesta, D-01):** una corrida adicional con los parámetros recomendados por el fabricante y tres semillas, para ver si las conclusiones dependen de la decodificación voraz.

## 5. Control experimental del laboratorio (portátil)

Antes de cada bloque de corridas:
1. `ollama ps` vacío (descargar otros modelos con `ollama stop <modelo>`; al auditar había `qwen3.5:9b` en carga híbrida y 3283 MiB de VRAM ocupados).
2. Equipo conectado a corriente, plan de energía fijo y documentado; sin otras aplicaciones que usen la GPU.
3. Registrar temperatura de GPU y frecuencia de inicio; esperar a que baje de un umbral fijado antes de iniciar (umbral por definir en el smoke test).
4. Registrar `nvidia-smi` (nombre, VRAM, driver), versión de Ollama, Python, SO y CPU (manifiesto, §6).
5. **Orden de las configuraciones intercalado** (p. ej., q4 → q8 → fp16 → fp16 → q8 → q4 entre repeticiones) para no confundir precisión con deriva térmica.
6. **No mezclar** corridas GPU-only con CPU/híbridas en una misma comparación de rendimiento; el modo se determina con `/api/ps` (`size_vram` frente a `size`) y se anota por corrida.

## 6. Registro por corrida

**Manifiesto de corrida** (un JSON por ejecución, `experiment_manifest.json`; solo se crea si hubo ejecución real):
fecha UTC; versiones de Python, Ollama y SO; GPU (nombre, VRAM, driver, CUDA) y CPU; modelo, etiqueta, **digest local**, cuantización y detalles de `/api/show`; modo de offload (`/api/ps`); dataset y su SHA-256; SHA-256 de configuración y de prompts; `prompt_version`, `rubric_version`; parámetros efectivos; commit de Git; temperatura de GPU al iniciar; plan de energía; condiciones de red.

**Registro por ítem** (`runs/*.jsonl`, cada línea): `run_id`, `rep`, `is_warmup`, `item_id`, `problem_base_id`, `task`; prompt completo y su hash; respuesta íntegra y `thinking`; `done_reason`; `error` con cuerpo HTTP; `wall_seconds`; y, **reportados por Ollama**: `total_duration`, `load_duration`, `prompt_eval_count`, `prompt_eval_duration`, `eval_count`, `eval_duration`.

**Separación obligatoria de procedencia:** cada métrica se rotula `reportada_por_ollama`, `medida_externa` o `derivada`. Tokens/s es derivada de los conteos y duraciones de Ollama; RAM/VRAM/potencia/temperatura solo son «medidas» si se muestrearon con una herramienta independiente. **No se fabrican ni se imputan datos.**

## 7. Métricas

| Bloque | Métrica | Método |
|---|---|---|
| `solve` | Exactitud | Extracción de la respuesta numérica y comparación con `gold_answer` calculado. Se revisan a mano los casos ambiguos o con formato inesperado |
| `solve` | Explicación (corrección, legibilidad, edad) | Rúbrica 0–2, revisión humana |
| `diagnose` | Acierto en «correcta/incorrecta» | Determinista frente a `student_answer_is_correct` (incluye controles negativos) |
| `diagnose` | Localización específica del error | Rúbrica 0–2 contra `gold_error_observable` |
| `hint` | Fuga de la respuesta | Detección determinista de `gold_answer` en la pista + revisión humana |
| `hint` | Utilidad y claridad apropiada a la edad | Rúbrica 0–2 por criterio |
| Costo | Tamaño en disco; carga; latencia total; tokens/s; TTFT; RAM/VRAM; potencia; temperatura | Según §3 y §6; separando reportado de medido |

No se usa un LLM como único juez de la calidad pedagógica.

## 8. Diseño de repeticiones y análisis

- **Calidad:** una pasada determinista por configuración (T=0). Se repite una segunda pasada para comprobar si las salidas son idénticas; si no lo son, se reporta la variabilidad y se usan más repeticiones.
- **Tiempos:** por configuración, 1 pasada de calentamiento descartada + **≥3 repeticiones medidas** (recomendado 5), intercaladas (§5). Se reportan mediana, rango intercuartílico, media y desviación estándar con *n* explícito. **3 repeticiones es el mínimo del protocolo, no una garantía estadística.**
- **Comparación:** emparejada por ítem entre precisiones. Los tres ítems de un problema base no son independientes: el análisis se agrupa por `problem_base_id` (*bootstrap* por conglomerados para intervalos de confianza). Para binarios, comparación pareada exacta (p. ej., McNemar); para rúbricas 0–2, diferencias emparejadas con intervalos. **El método final se decide con el mentor (D-03).**
- **Interpretación:** con ~30 problemas base los intervalos serán anchos; no se hacen afirmaciones causales ni de «no hay diferencia» sin potencia justificada. Una corrida funcional no es evidencia estadística.

## 9. Criterios de aceptación

**Hito 1 — prueba de humo (9 ítems × `qwen3:0.6b-q4_K_M`):** se considera superada solo si se cumplen todos:
1. El digest local coincide con `7df6b6e09427…`.
2. 9 registros JSONL válidos, 0 errores, sin truncamiento (`done_reason = stop`) o con los truncamientos reportados.
3. `think:false` verificado (campo `thinking` vacío y sin etiquetas `<think>`).
4. Manifiesto con hardware, versiones y **modo de offload** (si hay CPU/híbrido, se declara).
5. **Ejecución sin red** demostrada (adaptadores de red desactivados o modo avión) con el mismo resultado.
6. Registro crudo conservado, sin sobrescribir.

El smoke test **no** produce evidencia sobre calidad pedagógica ni sobre cuantización. Estado actual: **ejecutado el 2026-11-14 con `starter_v0.2`; 6 de 6 criterios cumplidos** (`smoke_test_report.md`).

**Hito 2 — dataset piloto:** 30 problemas base (o 90/84 ítems según D-06) con trazabilidad completa, rúbrica predefinida **antes** de mirar resultados y una muestra marcada para revisión docente.
**Hito 3 — cuantización:** las tres precisiones con condiciones idénticas, ≥3 repeticiones, manifiesto por corrida, análisis emparejado con intervalos.
**Hito 4 — mentor:** informe breve con preguntas abiertas; no presentar el piloto como resultado concluyente.

## 10. Lista previa a resultados publicables
- Edición curricular declarada con precisión, o confirmada con MEDUCA/docentes.
- Digest, licencia, método de cuantización y política de *thinking* documentados por modelo.
- Rúbrica y muestra de revisión docente definidas antes del análisis.
- Hardware real, backend y offload registrados.
- Datos sintéticos, revisados y resultados no validados, separados.
- Código y JSONL crudos conservados con manifiesto.

## 11. Limitaciones declaradas
Piloto sintético y pequeño; un solo modelo; laboratorio en PC (portátil); métricas de costo parcialmente reportadas por Ollama; sin revisión docente; currículo vigente sin confirmar; energía y térmico solo parciales en PC; multi-turno y paso correctivo diferidos.

## 12. Decisiones pendientes del mentor
D-01 (muestreo), D-02 (*thinking*), D-03 (muestra e incertidumbre), D-04 (edición curricular), D-05 (contribución principal), D-06 (controles negativos), D-07 (orden de las etapas de P0). Detalle en `audit.md` §2.
