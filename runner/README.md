# Starter v0.2 — prueba de humo (smoke test) AAAI-27 UC

**Estado: corrección del starter v0.1 (ver `CHANGES.md`). Probado solo con un Ollama simulado. Aún no ejecutado con un modelo real. No genera evidencia científica.**

## Qué hace
Hace 9 preguntas sintéticas de aritmética de 3.er grado a un modelo local de Ollama y guarda, sin sobrescribir nada:
- `runs/<fecha>_<modelo>_<id>.jsonl`: una línea por ítem, con la respuesta íntegra y los datos de Ollama.
- `runs/<mismo nombre>.manifest.json`: el manifiesto de la corrida (hardware, versiones, digest, dataset, modo GPU/CPU).

## Comandos (PowerShell, desde esta carpeta)

Pruebas del código (no necesitan Ollama):
```powershell
python -I -m unittest discover -s tests -v
```

Corrida de humo con los modelos de `D:\canada_work` (servidor en el puerto 11435 abierto):
```powershell
python src/run_experiment.py --model qwen3:0.6b-q4_K_M --host http://127.0.0.1:11435 --limit 3
```

Con los 9 ítems, quitando `--limit 3`. Si el servidor es el normal (11434), no hace falta `--host`.

## Antes de correr algo que vayas a medir
1. `ollama ps` (en el servidor que uses) vacío: sin otros modelos cargados.
2. Portátil conectado a corriente.
3. Para la prueba sin red: desactivar el Wi-Fi y repetir.

## Límites
- Una sola pasada sin calentamiento: no es evidencia de latencia ni de calidad.
- Las duraciones y conteos son de Ollama; la VRAM del modelo sale de `/api/ps` y la GPU de `nvidia-smi`. No se mide RAM ni energía.
- `src/make_review_sheet.py` es el original sin corregir y no es ciego: no usar para revisión formal.
- `docs/protocol.md` y `configs/model_inventory.csv` están obsoletos; ver `../docs/`.
