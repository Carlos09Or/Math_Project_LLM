# dataset_v0.1 — Aritmética de 3.er grado (Panamá), borrador sintético

**Estado: BORRADOR. Sintético, original, SIN revisión docente (`reviewer_status = unreviewed`). No declara alineación curricular validada ni validez pedagógica.**

## Qué contiene
- `data/items.jsonl`: **90 ítems** = 30 problemas base × 3 tareas (`solve`, `diagnose`, `hint`).
- `data/problem_bases.csv`: resumen de los 30 problemas base (operación, operandos, dificultad, generador de error, partición).
- Diseño y justificación: `../docs/dataset_design.md`.

## Composición
| Dimensión | Valor |
|---|---|
| Competencias (M-2024, ver `../docs/curriculum_map.csv`) | `A3-SUB-24` sustracción · `A3-MUL-24` multiplicación · `A3-DIV-24` división con residuo: 10 problemas cada una |
| Controles con respuesta correcta del estudiante | 6 problemas (2 por competencia) |
| Partición (por problema base) | `dev` 3 problemas (9 ítems, para ajustar prompts) · `pilot` 27 problemas (81 ítems, para evaluar) |
| Dificultad (regla objetiva en `src/generators.py`) | nivel 1: 5 problemas · nivel 2: 12 · nivel 3: 13. **Está sesgada hacia lo difícil**; reequilibrar con el mentor y docentes |
| Rangos numéricos | resta y multiplicación hasta 4 cifras; dividendos hasta 3 cifras y divisores de 1–2 cifras (dentro de lo que contempla M-2024; parte de M-2014) |

## Cómo se garantiza que las respuestas son correctas
- `gold_answer` se **calcula** con código a partir de `operation` y `operands`; no se escribe a mano.
- El error del estudiante se **produce con una regla determinista** (`error_generator`), por lo que `gold_error_observable` es verdadero por construcción.
- `src/validate_dataset.py` **recalcula todo** (respuesta, error, dificultad, esquema, particiones, enunciados) sin confiar en el archivo.
- Las pruebas incluyen casos calculados a mano antes de escribir el código, y comprueban que el validador detecta manipulaciones.

## Campos
Los 19 campos del protocolo v0.1, más los añadidos del diseño (`gold_error_observable`, `gold_error_type`, `student_answer_is_correct`, `error_generator`) y cuatro de apoyo para la verificación automática: `operation`, `operands`, `gold_answer_struct`, `student_answer_struct`.
Diferencias respecto a `../docs/dataset_design.md`: `competency_id` usa el sufijo de edición (`A3-SUB-24`, como en `curriculum_map.csv`) y `rubric_version` vale `rubric_v0.1_not_written` porque la rúbrica aún no existe.

## Comandos (PowerShell, desde esta carpeta)
```powershell
python -I -m unittest discover -s tests -v
python -I src/validate_dataset.py data/items.jsonl
```
Regenerar (el constructor nunca sobrescribe; borra antes los archivos de `data/` o usa otra carpeta):
```powershell
python -I src/build_dataset.py --output-dir otra_carpeta
```

## Límites y pendientes
1. **Sin revisión docente.** Pendiente: pertinencia de los problemas para 3.er grado, rangos numéricos y edición curricular (D-04), y que la taxonomía de errores sea real y frecuente. Las etiquetas `gold_error_type` son una **hipótesis**.
2. **No hay rúbrica todavía** (`rubric_v0.1.md`, siguiente hito). Sin ella no se puede puntuar `diagnose` ni `hint`.
3. **Los ítems `hint` de los 6 controles** (la respuesta del estudiante es correcta) piden una pista de verificación; si el mentor prefiere no usarlos, se filtran con `student_answer_is_correct = true` y quedan 84 ítems (D-06).
4. **El runner `starter_v0.2` todavía no lee este formato** (usa `id`/`problem`); hace falta un adaptador antes de correr este dataset.
5. **Contaminación:** los problemas son originales, pero números y situaciones simples pueden coincidir con datos públicos. No se afirma ausencia de contaminación (pendiente la búsqueda en GSM8K y MathDial).
6. Los enunciados no se han leído con un docente para vocabulario regional ni claridad.
