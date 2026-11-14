# results/ — Evidencia cruda de cada prueba

Aquí está lo que produjo cada prueba, para poder auditarla. El sitio web (`pruebas.html` y sus páginas de detalle) se genera **desde estos archivos** con `python tools/build_site_data.py`, así que ninguna cifra de la web está escrita a mano.

**Sobre los archivos:**
- Los `.jsonl` (una respuesta del modelo por línea, y las respuestas ya puntuadas) son **idénticos a los originales**: su SHA-256 no cambia.
- Los `.json` (manifiestos de corrida, matrices, resúmenes) tienen las **rutas locales redactadas** (usuario de Windows y carpetas) y llevan una clave `redaction_note`; su SHA-256 difiere del de los originales, que se conservan en el equipo del investigador.
- Una corrida funcional **no es evidencia estadística**. Ver cada informe para sus límites.

| Carpeta | Prueba | Qué contiene | Informe |
|---|---|---|---|
| `../runner/runs/` | **T1** Prueba de humo | 3 corridas del starter v0.2 (con red y sin red) y la evidencia de red | `../docs/smoke_test_report.md` |
| `gpu_capacity/` | **T2** Capacidad de la GPU | Un solo JSON: huella de 13 modelos, co-carga y concurrencia, con metadatos del equipo | `../docs/` y la página `capacidad-gpu.html` |
| `format_tuning_r1/` | **T3** Ajuste de formato, ronda 1 | 4 matrices (una por variante de prompt) sobre 12 problemas de práctica, y la decisión | `../docs/prompt_tuning_dev.md` |
| `format_tuning_r2/` | **T4** Ajuste de formato, ronda 2 | 4 matrices sobre 12 problemas de práctica **nuevos**, y la decisión (ganó `prompt-v0.5b`) | `../docs/prompt_tuning_dev_r2.md` |
| `pilot_qwen3_0.6b/` | **T5** Piloto | 972 registros (3 precisiones × 81 ítems × 4 pasadas), respuestas puntuadas, resumen e informe con intervalos | `../docs/pilot_run_plan.md` y `../docs/pilot_results_qwen3_0.6b.md` |
| `scorer_validation_dev/` | Validación del corrector | Primera corrida exploratoria sobre la partición `dev` que sirvió para auditar el corrector | `../runner/CHANGES.md` |

## Cómo leer los archivos
- `*_repN.jsonl` / `*_bloque.jsonl`: una línea por respuesta (`response`), con tiempos y conteos de tokens que reporta Ollama, `rep` (repetición) e `is_warmup` (el calentamiento se guarda pero no se puntúa).
- `*.manifest.json`: versiones, hardware, digest del modelo, huella del dataset y de la configuración, modo GPU/CPU y conteos de la corrida.
- `*.matrix.json`: el orden de las pasadas de una matriz de modelos (siempre en secuencia).
- `*.scores.jsonl`: las mismas respuestas con la puntuación del corrector determinista.
- `*.summary.json`, `*.report.json`, `*.txt`: resúmenes y el informe descriptivo del piloto.
- `format_tuning_decision*.json`: aplicación mecánica de la regla de decisión fijada antes de correr.

## Lo que estos datos **no** son
Calidad pedagógica (no hay rúbrica ni revisión humana), ni evidencia sobre otros modelos o dispositivos móviles. El dataset es sintético y no tiene validación docente.
