# roadmap.md — Fases y criterios para avanzar

**Fecha:** 2026-11-13 · **Estado:** propuesto; el orden y las puertas de decisión requieren el visto bueno del mentor. No se asignan fechas: dependen de revisión docente y de decisiones pendientes.
**Regla de avance:** no se pasa de fase sin cumplir los criterios de salida de la anterior. Un criterio no verificado cuenta como no cumplido.

## Vista general

| Fase | Nombre | Estado hoy | Depende de |
|---|---|---|---|
| F0 | Auditoría y fuentes | **Hecha en borrador** (este conjunto de documentos), pendiente de revisión | — |
| F1 | Smoke test (9 ítems × Q4) | **Completado** (2026-11-14; ver `smoke_test_report.md`) | — |
| F1.5 | Runner v0.3 | **Avanzada:** adaptador, calentamiento/repeticiones, corrector determinista y matriz secuencial hechos y probados (30 pruebas); faltan hoja de revisión ciega y rúbrica | Aprobación del mentor (D-08: formatos de salida del prompt) |
| F2 | Dataset piloto y rúbricas | **En curso:** borrador de 90 ítems generado y validado (`dataset_v0.1/`); faltan rúbrica y revisión docente | D-04, D-06; docentes |
| F3 | Cuantización (FP16/Q8_0/Q4_K_M) | No iniciada | F1.5, F2 |
| F4 | Instrumentación de costo (TTFT, RAM/VRAM, energía, térmico, llama.cpp) | No iniciada | F3 |
| F5 | Extensión de modelos | No iniciada | F3, F4 |
| F6 | Multi-turno y paso correctivo | No iniciada | F2, F3 |
| F7 | Android y modularidad | No iniciada | F4, D-05 |
| F8 | Adaptación (LoRA/QLoRA) | Condicional | F3–F6 |

---

## F0 — Auditoría y fuentes
- **Entregables:** `traceability_matrix.md`, `audit.md`, `sources_verification.md`, `dataset_design.md`, `curriculum_map.csv`, `experimental_protocol_v0.2.md`, este `roadmap.md`.
- **Criterios de salida:**
  1. El investigador revisó los hallazgos E, M y D.
  2. Está decidida la edición curricular de referencia (D-04) o queda declarada como provisional.
  3. El mentor respondió o priorizó las decisiones D-01 a D-07.
- **Pendiente:** verificaciones listadas en `sources_verification.md` §5.

## F1 — Smoke test
- **Objetivo:** demostrar que el *pipeline* completo corre de forma local y offline y deja registro crudo. **No** mide calidad ni cuantización.
- **Criterios de salida:** los seis del Hito 1 (`experimental_protocol_v0.2.md` §9). Entre ellos, digest correcto, 9 registros sin errores, `think:false` verificado, modo de offload registrado y ejecución sin red.
- **Si falla:** documentar la causa; no avanzar.

## F1.5 — Starter v0.2 (código corregido)
- **Alcance:** E-01 a E-04, E-08, E-09, M-01 a M-04, M-06; manifiesto de corrida; hoja ciega; pruebas mínimas; lock de dependencias; `.gitignore`.
- **Criterios de salida:** pruebas que pasan; el dataset de 9 ítems migrado al esquema de `dataset_design.md` con validador; corrida de humo repetida con el código v0.2; ningún archivo del starter original modificado.

## F2 — Dataset piloto y rúbricas
- **Objetivo:** 30 problemas base originales × 3 tareas (90 ítems, o 84 según D-06), con trazabilidad curricular.
- **Criterios de salida:**
  1. Rúbrica `rubric_v0.1` con ejemplos ancla, **fijada antes de mirar resultados**.
  2. 100 % de los ítems pasan el validador (respuestas recalculadas, errores generados por regla, particiones por problema base).
  3. Una muestra definida para revisión docente; el estado `reviewer_status` refleja lo realmente revisado.
  4. Plan de contaminación documentado.
  5. Ningún texto copiado de materiales protegidos.
- **Nota:** hasta la revisión docente, el dataset se rotula «sintético, sin validación docente».

## F3 — Cuantización controlada
- **Objetivo:** comparar FP16, Q8_0 y Q4_K_M del **mismo** Qwen3-0.6B en condiciones idénticas.
- **Criterios de entrada:** F1.5 y F2 completas; GPU libre; manifiesto por corrida.
- **Criterios de salida:** ≥3 repeticiones medidas por configuración tras calentamiento, intercaladas; análisis emparejado por ítem con intervalos agrupados por problema base; separación estricta de GPU-only y CPU/híbrido; resultados crudos conservados; primera frontera calidad–costo descriptiva; limitaciones explícitas.
- **Lo que NO se concluye aquí:** nada causal sobre otras familias ni sobre móviles.

## F4 — Instrumentación de costo
- **Contenido:** TTFT (*streaming* y `llama-bench`), RAM y VRAM medidas, potencia de GPU y temperatura con `nvidia-smi`, cuantización GGUF documentada con llama.cpp.
- **Criterios de salida:** cada métrica de costo rotulada como reportada, medida o derivada; método de muestreo documentado; diferencias entre Ollama y llama.cpp reportadas, no ocultadas.
- **Límite conocido:** energía total y térmico del sistema completo requieren instrumentos adicionales.

## F5 — Extensión de modelos
- **Candidatos:** Qwen3-1.7B, Gemma 3 1B, SmolLM3 3B, Phi-4-mini 3.8B; secundarios Llama 3.2 1B, DeepSeek-R1-Distill 1.5B, Gemma 270M, Qwen3 4B.
- **Criterios de entrada por modelo:** licencia leída desde la ficha oficial y registrada (`verified`); etiqueta con cuantización explícita y digest; verificación de que cabe o no en 6 GB (por ejemplo, Phi-4-mini FP16 con 7,7 GB no cabe).
- **Regla:** comparaciones entre familias declaradas como **no causales**; los modelos de razonamiento se evalúan con su propia política de *thinking*.

## F6 — Multi-turno y paso correctivo (P0)
- **Contenido:** tarea `correct_step`; diálogos de 2–5 turnos; coherencia entre turnos; degradación por longitud de diálogo.
- **Criterios de entrada:** F2 y F3 completas; esquema de diálogo y rúbrica específica definidos y revisados por docentes.
- **Criterios de salida:** resultados por turno; análisis separado del de una sola interacción.

## F7 — Android y diseño modular (P0)
- **Contenido:** perfiles de dispositivo Android o hardware reproducible con RAM y cómputo limitados; evaluación del diseño modular (contenido local + componentes deterministas + modelo solo para pistas y explicaciones).
- **Criterios de entrada:** F4 completa; D-05 resuelta por el mentor.
- **Criterios de salida:** mediciones en dispositivos o perfiles definidos; **única fase que puede sostener afirmaciones sobre móviles**.

## F8 — Adaptación (condicional)
- **Condición:** la línea base cuantizada muestra pérdida pedagógica relevante (H1/H2).
- **Contenido:** LoRA/QLoRA con conjunto curado; comparación de tres vías (sin adaptar / cuantizado / cuantizado + adaptado); particiones train/val/test por `problem_base_id`.
- **Criterios de entrada:** F3 completa; conjunto de adaptación independiente del de evaluación; análisis de contaminación.

---

## Decisiones que bloquean fases

| Decisión | Bloquea | Responsable |
|---|---|---|
| D-04 edición curricular de referencia | F2 | Mentor / docentes |
| D-06 controles negativos y 90 ítems | F2 | Mentor |
| D-01 muestreo y D-02 *thinking* | F1.5, F3 | Mentor |
| D-03 muestra e incertidumbre | F3 | Mentor |
| D-05 contribución principal | F7 | Mentor |
| D-07 orden de etapas de P0 | F6, F7 | Mentor |

## Riesgos transversales
1. **Currículo cambiante** (Plan Estratégico 2025–2029 prevé una segunda versión actualizada): declarar siempre qué edición se usó.
2. **Laboratorio en portátil:** *throttling* y carga compartida de GPU; mitigado con control de estado y orden intercalado.
3. **Muestra pequeña:** intervalos amplios; evitar conclusiones causales.
4. **Alcance de P0:** multi-turno, paso correctivo, TTFT, energía, térmico, Android y LoRA siguen en el plan; ninguna fase los elimina.
5. **Licencias:** MathTutorBench sin licencia resuelta; modelos con términos propios (Gemma, Llama).

## Preguntas para el mentor (priorizadas)
1. ¿Cuál es la contribución principal: efecto de la cuantización sobre la pedagogía, o el diseño modular con verificación determinista? (D-05)
2. ¿Qué tamaño mínimo de muestra y qué método de incertidumbre son adecuados? (D-03)
3. ¿Qué edición curricular se toma como referencia y con qué docentes se validan rúbricas? (D-04)
4. ¿Decodificación voraz o muestreo recomendado, y qué política de *thinking*? (D-01, D-02)
5. ¿Qué pruebas en Android son necesarias para sostener afirmaciones de utilidad en dispositivos limitados? (F7)
