# traceability_matrix.md — Matriz de trazabilidad completa

**Fecha:** 2026-11-13 · **Versión:** v1.0 (sustituye el borrador parcial) · **Estado:** propuesta para revisión del investigador y del mentor.
**Fuentes cruzadas:** [P0] propuesta AAAI-27 UC #52 · [Pr] Protocolo base v0.1 · [PM] prompt maestro · [St] starter v0.1 (leído completo, **no ejecutado**).
**Principio:** el alcance científico de P0 se conserva. «Etapa posterior» significa «se hará, en otra fase», no «se descarta».

## Leyenda de estado
| Estado | Significado |
|---|---|
| **Implementado** | Existe en el starter y su lectura es consistente con el requisito. No implica que se haya probado en ejecución. |
| **Parcial** | Existe, pero incompleto o con un defecto (ver `audit.md`). |
| **Pendiente (F#)** | No existe; se hará en la fase indicada. |
| **Etapa posterior (F#)** | Requisito de P0 que queda fuera del primer experimento; fase de entrada en `roadmap.md`. |
| **Decisión** | Requiere decisión del mentor antes de implementarse. |

## 1. Pregunta, alcance y datos

| ID | Requisito | Origen | Starter | Estado | Fase | Nota |
|---|---|---|---|---|---|---|
| R01 | Pregunta: configuración mínima modelo–hardware–sistema para tutoría offline en **móviles** | P0 pp. 1–2 | README menciona «posteriormente validar en Android» | Etapa posterior | F7 | El piloto en PC no valida móvil |
| R02 | 3.er grado, aritmética, español de Panamá | Pr §1–2; PM | 9 ítems de 3 temas; `locale` ausente | Parcial | F2 | Rangos del currículo: ver `sources_verification.md` §1.2 |
| R03 | Tarea `solve` | Pr §5 | `prompt_for` + 3 ítems | Parcial | F1.5 | Sin *scorer* determinista (M-06) |
| R04 | Tarea `diagnose` (error **observable**) | Pr §5 (P0 dice «probable») | `prompt_for` + 3 ítems | Parcial | F1.5 | `gold_error` ambiguo (E-06); sin controles negativos (E-07) |
| R05 | Tarea `hint` sin revelar la respuesta | P0; Pr §5 | `prompt_for` + 3 ítems | Parcial | F1.5 | Sin detector de fugas (M-06) |
| R06 | Explicación adecuada a la edad | P0 «Approach»/«Evaluation» | Dentro de `solve` (texto libre) | Pendiente | F2 | Criterio de rúbrica de explicación |
| R07 | **Paso correctivo siguiente** | P0 p. 2 | No existe | Etapa posterior | F6 | Se conserva; tarea `correct_step` |
| R08 | **Consistencia multi-turno** y degradación por longitud de diálogo | P0 «Evaluation»; Zhang 2026 | No existe (`messages` de 1 turno) | Etapa posterior | F6 | Requiere esquema de diálogo; se conserva |
| R09 | Esquema de datos de 19 campos | Pr §5; PM | 7 de 19 con el mismo nombre; 12 ausentes o con otro nombre | Parcial | F1.5/F2 | E-05 |
| R10 | Trazabilidad curricular (doc, versión, página) | Pr §3; PM | `source_reference` de texto libre, sin página, solo edición 2014 | Parcial | F2 | Existe M-2024 (E-12); `curriculum_map.csv` |
| R11 | Problemas originales; sin copia extensa de textos protegidos | Pr §3 | 9 ítems sintéticos | Implementado | — | Verificar al ampliar |
| R12 | Partición por `problem_base_id` | PM; Pr §5 | Sin campo `split` | Pendiente | F2 | Para F8 (adaptación) |
| R13 | Contaminación por benchmarks públicos | PM | No tratada | Pendiente | F2 | Plan en `dataset_design.md` §9 |
| R14 | Revisión docente de ítems y rúbricas | Pr §5; PM | `reviewer_status` ausente | Pendiente | F2 | Nada es «validado por docentes» |
| R15 | Adaptación de MathTutorBench | PM | No existe | Pendiente | F2 | Parcialmente adaptable; licencia sin resolver |

## 2. Evaluación de calidad

| ID | Requisito | Origen | Starter | Estado | Fase | Nota |
|---|---|---|---|---|---|---|
| R16 | Exactitud verificada de forma determinista | P0; Pr §6 | No hay *scorer* | Pendiente | F1.5 | M-06 |
| R17 | Rúbricas 0–2 (diagnóstico, utilidad de pista, claridad por edad, no-revelación) con ejemplos ancla | Pr §6; PM | Columnas `…_0_a_2` sin rúbrica | Parcial | F2 | `rubric_v0.1.md` (siguiente hito) |
| R18 | No usar solo un LLM como juez | PM | No usa ningún juez | Implementado | — | Mantener |
| R19 | Revisión humana ciega y doble anotación de una muestra | P0; Pr §6 | Hoja **no ciega** y sin enunciado | Parcial | F2 | E-04 |
| R20 | Accionabilidad de la retroalimentación; corrección de la explicación | P0 «Evaluation» | No existe | Pendiente | F2 | Criterios adicionales de rúbrica |

## 3. Inferencia, reproducibilidad y costo

| ID | Requisito | Origen | Starter | Estado | Fase | Nota |
|---|---|---|---|---|---|---|
| R21 | Qwen3-0.6B Q4_K_M como primer modelo | Pr §4; PM | `--model qwen3:0.6b-q4_K_M` | Implementado | F1 | Etiquetas y digests verificados en el registro |
| R22 | Comparación pareada FP16/Q8_0/Q4_K_M | Pr §1; P0 (8-bit y 4-bit) | Comandos en README, sin control de condiciones ni repeticiones | Parcial | F3 | E-01, M-09 |
| R23 | Mismo dataset, prompt, plantilla, *thinking*, temperatura, semilla, contexto, hardware y backend | PM; Pr §6 | Configuración fija; faltan `top_k/top_p/repeat_penalty` | Parcial | F1.5 | M-01; las plantillas coinciden entre los 3 tags (verificado) |
| R24 | Política de *thinking* fija | PM | `think:false` para `qwen3:` | Parcial | F1 | **Pendiente de probar** en Ollama 0.40.16 (D-02) |
| R25 | Registro por corrida (lista de 11 campos) | PM | Ver `audit.md` §3 | Parcial | F1.5 | E-03 |
| R26 | Distinguir lo reportado por Ollama de lo medido | PM; P0 | README lo declara; nada se mide fuera de Ollama | Parcial | F4 | M-08 |
| R27 | No mezclar GPU-only con CPU/híbrido | PM | No registra el modo de offload | Pendiente | F1.5 | E-03; `/api/ps` |
| R28 | ≥3 repeticiones con calentamiento y dispersión | PM; Pr §6 | `repeat_count` sin uso | Pendiente | F3 | E-01 |
| R29 | Resultados crudos preservados | PM | Modo `'w'` sobrescribe | Parcial | F1.5 | E-02 |
| R30 | Manifiesto del experimento | PM; Pr checklist | No existe | Pendiente | F1.5 | E-03 |
| R31 | Sin APIs de pago ni modelos en la nube | PM | Solo `127.0.0.1` | Implementado | — | Se demuestra con la prueba sin red (M-05) |
| R32 | **TTFT** | P0 «Evaluation» | No existe | Etapa posterior | F4 | Requiere *streaming* o llama.cpp |
| R33 | RAM pico, almacenamiento del modelo, VRAM | P0; Pr §6 | Sin medición; tamaño no registrado | Pendiente | F4 | Tamaño en disco conocido por el registro |
| R34 | **Energía y comportamiento térmico** | P0 «Evaluation» («donde los dispositivos lo permitan») | No existe | Etapa posterior | F4 (PC parcial) / F7 (Android) | Portátil: potencia de GPU con `nvidia-smi`; consumo total no medible sin instrumento externo |
| R35 | Latencia total, tokens/s, carga | P0; Pr §6 | Duraciones de Ollama por ítem | Implementado (reportado) | F1 | No son mediciones independientes |

## 4. Análisis, extensiones y etapas posteriores

| ID | Requisito | Origen | Starter | Estado | Fase | Nota |
|---|---|---|---|---|---|---|
| R36 | Frontera de Pareto calidad–costo | P0 «Evaluation»; Pr H3 | `pandas`/`matplotlib` listados, sin código | Pendiente | F3 | E-13 |
| R37 | Degradación por dificultad | P0 | Campo `difficulty` ausente | Pendiente | F2 | |
| R38 | Intervalos de incertidumbre, análisis emparejado | Pr §6 | No existe | Pendiente | F3 | D-03 |
| R39 | Varias familias de modelos | P0 («several open-weight SLMs»); Pr §4 | `model_inventory.csv` con defectos | Etapa posterior | F5 | No comparar familias como efecto causal de cuantización |
| R40 | Licencias verificadas antes de redistribuir | PM | Afirmaciones sin verificar | Parcial | F1.5/F5 | `sources_verification.md` §3 |
| R41 | Adaptación LoRA/QLoRA; comparación de tres vías (sin adaptar / cuantizado / cuantizado + adaptado) | P0 «Approach» (condicional) | No existe | Etapa posterior | F8 | Condicional a que la línea base muestre pérdida pedagógica |
| R42 | Perfiles Android o hardware reproducible con RAM y cómputo restringidos | P0 «Approach» | No existe | Etapa posterior | F7 | |
| R43 | Diseño modular: contenido local, componentes deterministas, LLM solo para pistas/explicaciones | P0 «Approach» (hipótesis) | No existe | **Decisión** | F7 | D-05 |
| R44 | Sin datos de menores; sin app; sin entrenamiento | PM; Pr §2 | Cumple | Implementado | — | |
| R45 | Pruebas básicas, README, comandos reproducibles | PM | README sí; pruebas, lock y `.gitignore` no | Parcial | F1.5 | E-13 |

## 5. Discrepancias entre fuentes

| Fuente | Afirmación | Estado | Resolución propuesta |
|---|---|---|---|
| P0 vs. [Pr] | Dispositivos móviles / PC | Simplificación declarada | Etiquetar «laboratorio PC»; Android en F7 |
| P0 vs. [Pr] | «Error probable» frente a «error observable» | Endurecimiento de la tarea | Mantener «observable»; justificarlo en la dataset card |
| P0 vs. [Pr] | Multi-turno, paso correctivo, TTFT, energía, térmico | Omitidos en el protocolo | **Conservados** (R07, R08, R32, R34) |
| P0 vs. [Pr] | Diseño modular como hipótesis frente a posible contribución principal | Riesgo de alcance | D-05; no cambiar sin decisión |
| [Pr] vs. [St] | «Tags oficiales verificados» | Ahora **verificado** en el registro (digests completos) | Cerrado |
| [Pr]/[St] vs. fuentes | Currículo: 2014/2017 | **Existe M-2024** (Decreto 53/2024); rangos distintos | D-04; `sources_verification.md` §1 |
| [Pr] vs. [St protocol] | 90 ítems frente a 30–90; nombres de campo; nombre del inventario | Inconsistencia | Un solo protocolo (v0.2) |
| [PM] vs. [Pr] | MathTutorBench solamente / sin MRBench | P0 cita también MRBench | Verificar MRBench (pendiente) |
| [Pr] vs. equipo | «RTX 3060 (6 GB)» | `nvidia-smi`: **RTX 3060 Laptop**, 6144 MiB | Registrar el nombre exacto |
| [St] vs. fuentes | `qwen3:4b` como Qwen3-4B | Es la variante 2507 de razonamiento | Usar etiquetas con cuantización explícita |

## 6. Riesgos de alcance
1. **Deslizar la contribución** hacia «diseño modular» sin decisión del mentor (R43).
2. **Perder requisitos de P0** (R07, R08, R32, R34) por no figurar en el protocolo: se mitiga con fase y criterio de entrada en `roadmap.md`.
3. **Currículo:** elegir la edición equivocada o declarar «alineación vigente» sin confirmación (D-04).
4. **Confundir** pruebas de laboratorio en un portátil con validez en dispositivos móviles.
5. **Interpretar** una corrida funcional de 9 ítems como evidencia estadística.
