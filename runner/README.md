# Runner v0.3 — ejecución local, repeticiones y corrector automático

**Estado: la prueba de humo (Hito 1) se completó con v0.2; v0.3 añade el adaptador al dataset nuevo, calentamiento/repeticiones, un corrector determinista y un orquestador de modelos. Validado con pruebas (30, Ollama simulado) y con una corrida real exploratoria sobre la partición `dev`. No genera evidencia científica por sí solo.**

## Piezas
| Archivo | Qué hace |
|---|---|
| `src/run_experiment.py` | Una corrida de un modelo: lee el dataset (antiguo o nuevo), `--split`, `--warmup`, `--repeats`, `--prompt-version`; guarda `*.jsonl` + `*.manifest.json` sin sobrescribir |
| `src/run_matrix.py` | Varios modelos **siempre en secuencia**, por bloques o intercalados (`--interleave`, ≤ 3 modelos); comprueba GPU libre y servidor vacío |
| `src/score.py` | Corrector determinista: exactitud de `solve`, veredicto de `diagnose`, fuga del resultado en `hint`; resumen por ítem con intervalos de Wilson |
| `scripts/smoke_offline.ps1` | Prueba de humo sin red (Hito 1) |

## Comandos (PowerShell, desde esta carpeta)
Pruebas del código (no necesitan Ollama):
```powershell
python -I -m unittest discover -s tests -v
```
Matriz sobre la partición `dev` (ajuste de prompts), tres precisiones de Qwen3-0.6B, en secuencia e intercaladas, con el servidor de `D:\canada_work` abierto en el puerto 11435:
```powershell
python src/run_matrix.py --models qwen3:0.6b-q4_K_M,qwen3:0.6b-q8_0,qwen3:0.6b-fp16 --host http://127.0.0.1:11435 --split dev --warmup 1 --repeats 3 --interleave
```
Al terminar imprime el comando para puntuar. Forma general:
```powershell
python src/score.py --run runs/ARCHIVO.jsonl --run runs/OTRO.jsonl --dataset ../dataset/data/items.jsonl
```

## Reglas que el código hace cumplir
- **Nunca en paralelo.** En esta GPU medimos que 3 modelos simultáneos reducen los tokens/s entre 44 % y 68 %; para costo y latencia eso invalida la comparación.
- **GPU libre.** `run_matrix.py` se detiene si el servidor tiene modelos cargados (usa `--unload-first`) o si la GPU está ocupada (`--allow-busy` invalida las mediciones de costo).
- **No sobrescribe** registros, manifiestos ni resultados puntuados.
- **Solo local.** Rechaza hosts que no sean de este equipo.
- **El calentamiento se registra pero no se puntúa** (`is_warmup = true`).
- **La partición por defecto es `dev`.** Evalúa en `pilot` solo con el prompt ya fijado, y no lo cambies después de ver sus resultados.
- **El corrector rechaza un dataset distinto** del que usó la corrida (comparando SHA-256).

## Qué mide y qué NO mide el corrector
| Tarea | Mide | No mide |
|---|---|---|
| `solve` | Si la respuesta final coincide con la calculada (línea `Respuesta final:`; si falta, un respaldo marcado como tal; si no se puede leer, **«sin extracción»**, nunca se adivina) | Calidad de la explicación |
| `diagnose` | Si el veredicto «correcta/incorrecta» coincide con la verdad: sensibilidad (ítems con error) y especificidad (controles) | Si localizó bien el error |
| `hint` | Si la pista contiene el resultado correcto (fuga) | Utilidad, claridad, progresión, edad |

La calidad pedagógica necesita **rúbrica y revisión humana** (pendientes). Las tasas se calculan **por ítem** (las repeticiones de un ítem no son observaciones independientes) y se muestran dos: sobre lo que se pudo leer y una **estricta** que cuenta «sin extracción» como fallo. Los intervalos de Wilson son descriptivos y no consideran la agrupación por problema base; el método final se decide con el mentor (D-03).

## Límites
- Una corrida funcional no es evidencia estadística. Con la partición `dev` (3 problemas) cada celda tiene n efectivo = 3 ítems.
- Las duraciones son estadísticas de Ollama; la VRAM sale de `/api/ps` y la GPU de `nvidia-smi`. No se mide RAM ni energía.
- `src/make_review_sheet.py` es el original sin corregir y no es ciego: no usar para revisión formal.
- `docs/protocol.md` y `configs/model_inventory.csv` son copias obsoletas del v0.1; ver `../docs/`.
