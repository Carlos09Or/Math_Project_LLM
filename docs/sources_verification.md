# sources_verification.md — Fuentes verificadas

**Fecha de verificación:** 2026-11-13 · **Estado del documento:** borrador v0.1 para revisión del investigador y del mentor.

## Convención de estado
| Etiqueta | Significado |
|---|---|
| **VERIFICADO** | Leído directamente por mí en el documento o registro oficial (con página o digest). |
| **VERIFICADO-PARCIAL** | Reportado por un agente de lectura web y no releído por mí, o leído solo en parte. |
| **INFERIDO** | Deducido de evidencia indirecta (p. ej., digests idénticos); no lo declara la fuente. |
| **PENDIENTE** | No verificado todavía. |

Nota de método: los agentes de lectura web no pudieron extraer texto de los PDF de MEDUCA (devolvieron bytes). Descargué las copias y las leí yo con PyMuPDF. Un resumen automático afirmó que el PDF de 2017 «no parece el documento descrito»; es incorrecto: el PDF tiene 62 páginas y dice «VERSIÓN PARA VALIDACIÓN» en la página 1.

---

## 1. Currículo MEDUCA (Matemática, 3.er grado)

### 1.1 Documentos leídos

| ID | Documento | Entidad | Edición / versión impresa | Páginas | Estado |
|---|---|---|---|---|---|
| **M-2014** | *Programa de Tercer Grado, Educación Básica General — Actualización 2014* | MEDUCA, Dirección Nacional de Currículo y Tecnología Educativa | «Actualización 2014» (portada). Metadatos PDF: creado 2013-12-02. | 287 págs. PDF (apaisado). Matemática empieza en pág. impresa 143 (PDF 148); pág. impresa = PDF − 5. | VERIFICADO |
| **M-2017** | *Aprendizajes fundamentales en Matemática* (el título aparece en la pág. 7) | MEDUCA (Dir. Nac. de Currículo y Tecnología Educativa y otras direcciones; consultores BID, pág. 2) | Pág. 1: «VERSIÓN PARA VALIDACIÓN». Pág. 2: «31 de mayo de 2017». | 62 págs. 3.er grado: págs. 24–30. Tabla de progresión: págs. 4–5. | VERIFICADO |
| **M-2024** | *Programa de tercer grado, Educación Básica General — 2024* | MEDUCA, Dirección Nacional de Currículo y Tecnología Educativa | «2024». Metadatos PDF: creado 2023-10-19, modificado 2024-02-21. | 272 págs. Matemática: págs. impresas 167–232 (PDF 169–234); pág. impresa = PDF − 2. | VERIFICADO |
| **D-53** | *Decreto Ejecutivo n.º 53 del 23 de mayo de 2024* | Ministerio de Educación / Presidencia | Aprueba «la actualización e incorporación de los contenidos académicos» a los programas de Primaria (1.º–6.º) y Premedia, incluidos Matemática 1.º–6.º (Art. 1, tabla). | 5 págs. (escaneo, solo imagen). Leí las págs. 1–2; **las págs. 3–5 no se leyeron**. | VERIFICADO-PARCIAL |
| **PE-2025** | *Plan Estratégico 2025–2029* | MEDUCA | PDF creado 2026-04-27; la fecha de modificación en el servidor es 2026-04-28 | 68 págs. Relevantes: 14, 19, 20, 21. | VERIFICADO |

URLs:
- M-2014: https://meduca.gob.pa/wp-content/uploads/2025/04/programas-educacion-basica-general-primaria-3-2014.pdf
- M-2017: https://meduca.gob.pa/wp-content/uploads/2025/04/Panama_matematicas_31-de-mayo.pdf
- M-2024: https://guias.meduca.gob.pa/sites/default/files/2024-02/programa-tercero-web.pdf
- D-53: https://guias.meduca.gob.pa/sites/default/files/2024-06/decreto%2053.pdf
- PE-2025: https://www.meduca.gob.pa/wp-content/uploads/2026/04/Plan_Estrategico_2025-2029_final.pdf

SHA-256 de las copias locales (para trazabilidad): M-2014 `1de8249c…`, M-2017 `ec5f8824…`, M-2024 `dcc8f874…`, D-53 `d8ed153c…`, PE-2025 `74052acd…`.

### 1.2 Hallazgo principal: hay tres ediciones con rangos numéricos distintos
El protocolo v0.1 y el starter citan solo M-2014 y M-2017. **Existe una edición 2024 posterior (M-2024) respaldada por el Decreto 53/2024.** Los rangos para 3.er grado difieren de forma sustancial:

| Aspecto | M-2014 (págs. impresas) | M-2017, versión para validación (págs.) | M-2024 (págs. impresas) |
|---|---|---|---|
| Rango de números naturales | Objetivo de grado: hasta 100 000 (p. 148). El «objetivo de aprendizaje» de p. 149 dice hasta 10 000: **inconsistencia interna del documento**. | Hasta cinco cifras, 99 999 (pp. 4, 24) | Menores de 1 000 000 (pp. 174, 176) |
| Adición | Sumandos de 5 cifras, llevando y sin llevar (p. 153) | Hasta 5 cifras (p. 26) | Totales < 1 000 000; hasta 3 sumandos, al menos uno de 6 cifras (pp. 184–185) |
| Sustracción | Minuendo de 5 y 6 cifras, sin pedir y pidiendo (p. 154) | Hasta 5 cifras (p. 26) | Minuendos < 1 000 000, sin pedir y pidiendo prestado (pp. 186–189) |
| Multiplicación | Tablas del 6 al 9; 4 cifras × 2–3 dígitos (pp. 155–156) | «Hasta tres cifras» (p. 27) | Tablas del 10 al 12; ×10/100/1000; por decenas completas; 4 cifras × 2–3 dígitos (pp. 188–191) |
| División | Dividendo de 3 cifras con cero en las decenas ÷ 1 cifra; exacta/inexacta (pp. 157–158) | «Hasta tres cifras» (p. 27) | Exacta/inexacta; dividendos hasta 3 cifras, divisores de 1 o 2 cifras; propiedad reintegrativa (pp. 192–197) |
| Fracciones | Incluye multiplicación/división de fracciones, potenciación, radicación y decimales hasta millonésimos (pp. 161–165) | Suma/resta de homogéneas (p. 28) | Tipos, conversión mixto/impropia, semirrecta (pp. 198–203…); alcance de operaciones **no leído completo** |

Consecuencias: (a) los 9 ítems del starter (6×4, 36÷6, 125−38) están por debajo de los rangos en las tres ediciones; sirven como prueba técnica, no como muestra curricular; (b) la elección de la edición de referencia cambia la dificultad del benchmark (**decisión para el mentor, D-04 en `audit.md`**).

### 1.3 ¿Cuál es el currículo vigente en 2026?
- **VERIFICADO:** el Decreto 53/2024 aprueba la actualización de los programas de Matemática 1.º–6.º; M-2024 es la edición más reciente que encontré para 3.er grado.
- **INFERIDO:** que el PDF M-2024 sea el «Programa de estudio de Matemática 3.º» al que se refiere el decreto. El decreto lista programas por asignatura y grado, pero no nombra el archivo. El portal `guias.meduca.gob.pa` publica el decreto junto con los programas de 2024.
- **VERIFICADO (PE-2025, p. 19):** el plan prevé, para 2026, «Revisión y Renovación de los Planes de Estudios de la Básica General», el inicio de la validación con docentes y un «Rediseño cíclico… (2ª versión actualizada)». Para 2027 prevé validación participativa con al menos el 10 % de los docentes. Para 2026 prevé también distribuir 9 textos de Panamática para docentes de matemáticas, «para los nuevos programas actualizados de matemáticas».
- **PENDIENTE:** si en 2026 se publicó una segunda versión que reemplace a M-2024, y qué programa aplican hoy las escuelas. **No afirmar alineación con el currículo vigente** hasta confirmar con MEDUCA o con docentes.
- **VERIFICADO-PARCIAL:** la página `planes-y-programas-de-estudio` (reportada por un agente) lista «Programas Curriculares – Edición 2014», incluida Primaria 3.er grado, y no muestra entradas de 2024. El portal `guias.meduca.gob.pa` (sí lo muestra) lista el Decreto 53 y los programas de 2024. Ambos portales coexisten; ninguno declara cuál es el vigente.
- **PENDIENTE:** *Panamática Tercer Grado Docente* (https://guias.meduca.gob.pa/sites/default/files/2025-05/2025-GD-Panamatica%203-web.pdf, 25,9 MB, no abierto). El portal no explica qué es Panamática; por el contexto es una guía didáctica de Matemática, pero no está verificado.

---

## 2. MathTutorBench

| Ítem | Hallazgo | Estado |
|---|---|---|
| Repositorio | https://github.com/eth-lre/mathtutorbench · creado 2025-02-20 · último push 2026-08-27 · último commit `6faed173ec` («Add support for vllm thinking models.») · no archivado · 48 estrellas | VERIFICADO (API de GitHub) |
| Artículo | Macina et al., *MathTutorBench*, EMNLP 2025 (Main), pp. 204–221; arXiv 2502.18940 | VERIFICADO-PARCIAL (agente) |
| **Licencia** | **Sin resolver.** La API de GitHub devuelve `license: null`; no hay archivo `LICENSE` en `main` (404). El README y el sitio dicen CC BY-SA 4.0 (pie); la insignia del README dice CC BY 4.0, según el agente. | VERIFICADO (ausencia de LICENSE) / PENDIENTE (cuál aplica) |
| Habilidades | Tres: *Math Expertise*, *Student Understanding*, *Pedagogy* | VERIFICADO-PARCIAL |
| Tareas | Resolución de problemas (exactitud, GSM8K); preguntas socráticas (BLEU); corrección de la solución del estudiante (F1); localización del error (micro-F1); corrección del error (exactitud); generación de andamiaje y seguimiento de instrucciones pedagógicas (tasa de victoria con un modelo de recompensa), cada una con variante «difícil» | VERIFICADO-PARCIAL |
| Evaluador | Cinco tareas con métricas deterministas. Cuatro tareas de pedagogía usan un modelo de recompensa (Qwen2.5-1.5B afinado). El benchmark no usa un LLM como juez | VERIFICADO-PARCIAL |
| Idioma y nivel | Datos fuente en inglés (GSM8K, MathDial, Bridge, StepVerify); nivel de primaria superior/secundaria. El idioma no se declara explícitamente en lo leído | VERIFICADO-PARCIAL |
| Ejecución local | `python main.py --tasks <config>.yaml --provider completion_api …`; modelos locales vía vLLM (API compatible con OpenAI). **No documenta Ollama** en lo leído. Valores por defecto: temperatura 0.0, 2048 tokens | VERIFICADO-PARCIAL |

**Qué se puede adaptar y qué no (propuesta, sujeta a la licencia):**
- *Adaptable como diseño:* la taxonomía de habilidades (resolver / entender al estudiante / guiar); la estructura de «ubicar el error» y «corregir el error»; las métricas deterministas (exactitud, F1) en tareas con respuesta numérica verificable.
- *No adaptable tal cual:* el modelo de recompensa pedagógica (entrenado y validado en inglés, nivel secundaria; no hay evidencia de que funcione en español de 3.er grado); los datos fuente; la métrica BLEU para preguntas socráticas.
- *No copiar* datos ni código hasta resolver la licencia. Los datos nuestros serán originales.
- *Pendiente:* inspeccionar `configs/` y `tasks/` para ver los analizadores de respuestas; verificar la licencia de los conjuntos fuente.

**Otras referencias de la propuesta P0** (Nguyen 2024; Lu 2025; Zhou 2025; Zhang 2026; Maurya 2025 «MRBench»): **PENDIENTE** de verificación; solo las he leído como citas dentro de la propuesta.

---

## 3. Modelos en Ollama: etiquetas, digests, tamaños, licencias

### 3.1 Qwen3-0.6B (modelo primario) — verificado contra el registro de Ollama

Consulta directa a `registry.ollama.ai` (manifiestos y blobs públicos). Las etiquetas existen con la ortografía exacta del protocolo.

| Etiqueta | Digest del manifiesto (SHA-256, completo) | Peso del modelo (bytes) | Cuantización (página de Ollama) | Contexto en Ollama |
|---|---|---|---|---|
| `qwen3:0.6b-q4_K_M` | `7df6b6e09427a769808717c0a93cadc4ae99ed4eb8bf5ca557c90846becea435` | 522 640 096 | Q4_K_M | 40K |
| `qwen3:0.6b-q8_0` | `f6358994266d548dc070c564d49588fa3a6fac0cccd196bef38128aaa6ed22f3` | 832 278 240 | Q8_0 | 40K |
| `qwen3:0.6b-fp16` | `626c9556a80fcb9c30ebd28292edf465ccda990282c5fb1e680d106d23bacc1c` | 1 509 347 040 | F16 | 40K |
| `qwen3:0.6b` (etiqueta por defecto) | igual que `…q4_K_M` | 522 640 096 | **Q4_K_M** (mismo digest; la página no lo rotula) | 40K |

- **VERIFICADO:** los tres tags comparten el mismo bloque de plantilla (`ae370d884f10…`), licencia (`d18a5cc71b84…`) y parámetros (`cff3f395ef37…`). Esto apoya el control de «mismo prompt/plantilla» entre precisiones.
- **VERIFICADO:** parámetros por defecto en la etiqueta de Ollama: `temperature 0.6, top_k 20, top_p 0.95, repeat_penalty 1`, y tokens de parada `<|im_start|>`, `<|im_end|>`. El starter fija `temperature=0` y `seed=42` y **no registra** `top_k`/`top_p`/`repeat_penalty` (heredan estos valores).
- **VERIFICADO-PARCIAL (agente):** la licencia incluida en cada etiqueta es Apache-2.0; la ficha de Hugging Face `Qwen/Qwen3-0.6B` declara `apache-2.0`; el modelo tiene unos 752 M de parámetros según la página de Ollama.
- **VERIFICADO-PARCIAL (agente, ficha HF):** el modo *thinking* está activo por defecto; `enable_thinking=False` lo desactiva. Muestreo recomendado: razonamiento T=0.6, top_p=0.95, top_k=20; sin razonamiento T=0.7, top_p=0.8, top_k=20. La ficha advierte «DO NOT use greedy decoding» (en el contexto del modo con razonamiento). El contexto en HF es 32 768, y la página de Ollama muestra 40K: discrepancia **PENDIENTE** de explicar.
- **Los digests en el equipo local:** `qwen3:0.6b-*` **no está descargado** (`ollama list` solo muestra otros modelos). El digest efectivo local y las propiedades `ollama show` quedan **PENDIENTE** hasta el `pull`.

### 3.2 Candidatos de extensión
Fuente: páginas de Ollama y Hugging Face leídas por un agente el 2026-11-13. **VERIFICADO-PARCIAL.** Los prefijos de digest vienen de esas páginas, no de mis consultas al registro.

| Modelo | Etiqueta | Digest (prefijo) / tamaño | Licencia | Observaciones críticas |
|---|---|---|---|---|
| Qwen3-1.7B | `qwen3:1.7b-q4_K_M` | `8f68893c685c` / 1,4 GB | Apache-2.0 (blob de licencia) | q8_0: 2,2 GB; fp16: 4,1 GB |
| Gemma 3 1B | `gemma3:1b` | `97558784bdc9` / 806 MB, 32K | Términos de Gemma (`gemma`), repositorio HF con acceso restringido; incluye política de uso prohibido (no leída) | Igual digest que `1b-it-q4_K_M`: **INFERIDO** Q4_K_M. La etiqueta `gemma3` por defecto es el modelo de **4B**, no el de 1B |
| Gemma 3 270M | `gemma3:270m` | `e7d36fb2c3b3` / 292 MB | Términos de Gemma | Mismo digest que `270m-it-q8_0` (INFERIDO) |
| Llama 3.2 1B | `llama3.2:1b` | `baf6a787fdff` / 1,3 GB, 128K | **No mostrada en Ollama.** Licencia comunitaria de Meta: **PENDIENTE** de leer en Meta | Digest igual a `1b-instruct-q8_0` (INFERIDO: la etiqueta por defecto es Q8_0, no Q4) |
| Phi-4-mini 3.8B | `phi4-mini` | `78fad5d182a7` / 2,5 GB | MIT (ficha HF) | Etiqueta por defecto = `3.8b-q4_K_M` (INFERIDO). **`3.8b-fp16` pesa 7,7 GB: no cabe en 6 GB de VRAM.** Ollama muestra contexto 4K para q8_0 y fp16 frente a 128K del defecto |
| DeepSeek-R1-Distill 1.5B | `deepseek-r1:1.5b` | `e0979632db5a` / 1,1 GB | Pesos MIT; base Qwen-2.5 con licencia Apache-2.0 (página de Ollama) | Base exacta no nombrada en la página. Modelo de razonamiento: requiere política de *thinking* distinta |
| SmolLM3 3B | `hf.co/ggml-org/SmolLM3-3B-GGUF:Q4_K_M` | Q4_K_M 1,92 GB; Q8_0 3,28 GB; F16 6,16 GB | Apache-2.0 | Español entre los 6 idiomas nativos. *Thinking* activo por defecto (`/no_think`). **F16 (6,16 GB) excede la VRAM de 6 GB** |
| Qwen3-4B | `qwen3:4b` | `359d7dd4bcda` / 2,5 GB, 256K | Apache-2.0 | **El digest coincide con `4b-thinking-2507-q4_K_M`.** El `qwen3:4b` por defecto es la variante 2507 de razonamiento, no el Qwen3-4B híbrido original (`qwen3:4b-q4_K_M`, `2bfd38a7daaf`, 40K). Un `qwen3:4b` con ID `359d7dd4bcda` **sí está instalado en tu equipo** (VERIFICADO con `ollama list`) |

**Existencia de las etiquetas (VERIFICADO en el registro, 2026-11-13) y discrepancia de digests.** Comprobé en `registry.ollama.ai` (y en `huggingface.co` para SmolLM3) que existen: `qwen3:1.7b-q4_K_M` (1,36 GB), `qwen3:1.7b-q8_0` (2,22 GB), `qwen3:1.7b-fp16` (4,07 GB), `qwen3:4b-q4_K_M` (2,62 GB), `gemma3:1b-it-q4_K_M` (0,81 GB), `gemma3:1b-it-q8_0` (1,07 GB), `gemma3:270m-it-q8_0` (0,29 GB), `phi4-mini:3.8b-q4_K_M` (2,49 GB), `llama3.2:1b-instruct-q4_K_M` (0,81 GB), `llama3.2:1b-instruct-q8_0` (1,32 GB), `deepseek-r1:1.5b-qwen-distill-q4_K_M` (1,12 GB) y `hf.co/ggml-org/SmolLM3-3B-GGUF:Q4_K_M` (1,92 GB). **Corrección (2026-11-13, tras las descargas):** en una versión anterior de esta nota afirmé que los digests leídos de las páginas web no coincidían con el registro. **Era un error mío:** mi cálculo del hash del manifiesto con otras etiquetas no es fiable (coincidió con Qwen3-0.6B, que además verifiqué contra `/api/tags` local, pero no con otras). Los ID que muestra `ollama list` en tu equipo tras el `pull` **coinciden con los de las páginas web** en los 13 modelos: `qwen3:0.6b-q4_K_M` 7df6b6e09427, `…-q8_0` f6358994266d, `…-fp16` 626c9556a80f, `qwen3:1.7b-q4_K_M` 8f68893c685c, `…-q8_0` 29b6a7a420a4, `…-fp16` e9354f6174db, `qwen3:4b-q4_K_M` 2bfd38a7daaf, `gemma3:1b-it-q4_K_M` 97558784bdc9, `gemma3:270m-it-q8_0` e7d36fb2c3b3, `phi4-mini:3.8b-q4_K_M` 78fad5d182a7, `llama3.2:1b-instruct-q4_K_M` 22bc6b92eb01, `deepseek-r1:1.5b-qwen-distill-q4_K_M` e0979632db5a, `hf.co/ggml-org/SmolLM3-3B-GGUF:Q4_K_M` 19f83d5d424a (este último no estaba en la página; viene de tu `ollama list`). **Regla:** el digest válido es el que muestre `ollama list` (o `/api/tags`) tras el `pull`, y se registra en el manifiesto de la corrida. Los tamaños de la lista anterior sí vienen de mi consulta al registro.

Implicaciones para el starter: `model_inventory.csv` lista etiquetas por defecto (`gemma3:1b`, `llama3.2:1b`, `phi4-mini`, `deepseek-r1:1.5b`, `qwen3:4b`) con cuantizaciones distintas entre sí y con variantes cambiadas. **No pueden compararse como «mismo nivel de cuantización» ni mezclarse con la comparación de Qwen3-0.6B.** Las etiquetas deben fijarse con cuantización explícita y digest.

---

## 4. Entorno local (VERIFICADO con comandos, 2026-11-13)

| Elemento | Valor |
|---|---|
| GPU | NVIDIA GeForce **RTX 3060 Laptop GPU**, 6144 MiB, driver 581.42, CUDA 13.0 (`nvidia-smi`) |
| CPU / RAM | Intel Core i7-12700H, 14 núcleos / 20 hilos; 15,7 GB |
| SO | Windows 11 Home 10.0.26300 |
| Python | 3.12.6 |
| Ollama | 0.40.16 (`/api/version`); `OLLAMA_MODELS=D:\llm\ollama-models` |
| Proxy | Sin variables de proxy; WinHTTP «acceso directo» |
| **Estado de la GPU en el momento de la consulta** | `qwen3.5:9b` cargado, `size_vram` ≈ 2,99 GB de 6,67 GB (**carga híbrida GPU/CPU**), `memory.used` = 3283 MiB. **Cualquier medición debe empezar con la GPU libre.** |
| Modelos instalados | `gemma4:e4b`, `qwen3.5:9b`, `gemma4:e2b`, `lfm2.5:8b`, `llama3.1:8b`, `qwen3.5:2b`, `ministral-3:3b`, `qwen3:4b`, `qwen3.5:4b`. **No** está `qwen3:0.6b-*` |

---

## 5. Lo que queda pendiente
1. Confirmar con MEDUCA o docentes qué programa de Matemática de 3.º se aplica en 2026 (M-2024 frente a una posible 2.ª versión).
2. Leer las págs. 3–5 del Decreto 53 (vigencia, otros artículos).
3. Abrir *Panamática Tercer Grado Docente* (2025).
4. Leer el contenido de fracciones de M-2024 (págs. 198–232) si se incluyen fracciones.
5. Resolver la licencia de MathTutorBench y de sus conjuntos fuente.
6. Leer la licencia comunitaria de Llama 3.2 y la política de uso de Gemma (si esos modelos entran).
7. Verificar las referencias de la propuesta P0 (Lu 2025, Zhou 2025, Zhang 2026, MRBench).
8. Registrar digest y detalles locales de Qwen3-0.6B tras el `pull` (`ollama show`).
9. Aclarar la discrepancia de contexto 32 768 (HF) frente a 40K (Ollama).
