"""Ejecuta varios modelos SOBRE EL MISMO dataset, SIEMPRE EN SECUENCIA (nunca en paralelo).

Por qué en secuencia: en la RTX 3060 Laptop medimos que correr 3 modelos a la vez reduce los tokens/s entre
44 % y 68 % y aplana las diferencias entre precisiones. Para costo y latencia eso invalida la comparación.

Modos:
  por bloques (defecto): modelo A (calentamiento + repeticiones), descarga A, modelo B, ...
  --interleave         : repetición 1 de A, B, C; repetición 2 rotada (B, C, A); ... Requiere <= 3 modelos
                         (el servidor de Ollama mantiene como máximo 3 cargados). Reduce el sesgo por deriva térmica.

Uso:
  python src/run_matrix.py --models qwen3:0.6b-q4_K_M,qwen3:0.6b-q8_0,qwen3:0.6b-fp16 \
      --host http://127.0.0.1:11435 --split dev --warmup 1 --repeats 3 --interleave
La partición por defecto es 'dev' (ajuste de prompts). Evalúa en 'pilot' solo con el prompt ya fijado.
"""
import argparse
import json
import pathlib
import sys
import uuid

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import run_experiment as rx  # noqa: E402

ROOT = rx.ROOT
DEFAULT_DATA = ROOT.parent / 'dataset' / 'data' / 'items.jsonl'
GPU_BUSY_MIB = 1500  # por encima de esto con el servidor vacío, otra cosa usa la GPU
MAX_LOADED = 3       # valor por defecto de Ollama, verificado en este equipo


def loaded_models(host):
    return [m.get('name') for m in rx.request_json(host + '/api/ps', timeout=15).get('models', [])]


def unload(host, name):
    try:
        rx.request_json(host + '/api/generate', {'model': name, 'keep_alive': 0}, timeout=60)
    except (RuntimeError, OSError, ValueError):
        pass


def unload_all(host):
    for n in loaded_models(host):
        unload(host, n)


def gpu_used_mib():
    snap = rx.gpu_snapshot()
    if not snap or not snap['gpus']:
        return None
    return max(int(g['memory_used_mib']) for g in snap['gpus'])


GPU_WAIT_TIMEOUT = 60.0  # segundos que se espera a que la GPU se libere tras descargar modelos
GPU_WAIT_POLL = 1.5


def wait_gpu_free(host, limit_mib):
    """Espera a que el servidor esté vacío y la memoria de la GPU baje del umbral (la descarga no es instantánea).
    Devuelve el último valor de memoria usada (MiB) o None si no hay nvidia-smi."""
    import time
    deadline = time.monotonic() + GPU_WAIT_TIMEOUT
    while True:
        used = gpu_used_mib()
        if not loaded_models(host) and (used is None or used <= limit_mib):
            return used
        if time.monotonic() >= deadline:
            return used
        time.sleep(GPU_WAIT_POLL)


def plan_passes(models, repeats, warmup, interleave):
    """Lista de pasadas (modelo, warmup, repeats, rep_start). Pura; se prueba sin Ollama."""
    if not interleave:
        return [{'model': m, 'warmup': warmup, 'repeats': repeats, 'rep_start': 1} for m in models]
    out = []
    n = len(models)
    for r in range(1, repeats + 1):
        k = (r - 1) % n
        for m in models[k:] + models[:k]:  # rotación tipo cuadrado latino
            out.append({'model': m, 'warmup': warmup if r == 1 else 0, 'repeats': 1, 'rep_start': r})
    return out


def parse_args(argv):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument('--models', required=True, help='etiquetas de Ollama separadas por coma')
    p.add_argument('--host', default=rx.DEFAULT_HOST)
    p.add_argument('--data', default=str(DEFAULT_DATA))
    p.add_argument('--config', default=str(ROOT / 'configs' / 'experiment.json'))
    p.add_argument('--split', choices=rx.SPLITS, default='dev')
    p.add_argument('--prompt-version', choices=rx.PROMPT_VERSIONS, default=rx.FROZEN_PROMPT_VERSION,
                   help='por defecto, el prompt congelado para la evaluación')
    p.add_argument('--tasks', default='solve,diagnose,hint', help='tareas a ejecutar (se pasa al runner)')
    p.add_argument('--warmup', type=int, default=1)
    p.add_argument('--repeats', type=int, default=3)
    p.add_argument('--limit', type=int, default=None)
    p.add_argument('--interleave', action='store_true')
    p.add_argument('--runs-dir', default=str(ROOT / 'runs'), help='carpeta de salida de registros y manifiestos')
    p.add_argument('--unload-first', action='store_true', help='descarga los modelos ya cargados en el servidor antes de empezar')
    p.add_argument('--allow-busy', action='store_true', help='permite empezar aunque la GPU esté ocupada (invalida mediciones de costo)')
    a = p.parse_args(argv)
    a.model_list = [m.strip() for m in a.models.split(',') if m.strip()]
    if not a.model_list or len(set(a.model_list)) != len(a.model_list):
        p.error('--models necesita al menos un modelo y sin repetidos')
    if a.warmup < 0 or a.repeats < 1:
        p.error('--warmup >= 0 y --repeats >= 1')
    return a


def main(argv=None):
    a = parse_args(sys.argv[1:] if argv is None else argv)
    host = rx.normalize_host(a.host)
    if not rx.is_loopback(host):
        raise SystemExit(f'Host no local ({host}). El experimento es offline.')
    if a.interleave and len(a.model_list) > MAX_LOADED:
        raise SystemExit(f'--interleave admite como máximo {MAX_LOADED} modelos (límite de modelos cargados a la vez).')

    try:
        tags = {m.get('name') for m in rx.request_json(host + '/api/tags', timeout=30).get('models', [])}
        busy = loaded_models(host)
    except (RuntimeError, OSError, ValueError) as e:
        raise SystemExit(f'No se pudo conectar con Ollama en {host}: {e}')
    missing = [m for m in a.model_list if m not in tags]
    if missing:
        raise SystemExit(f'Modelos no instalados en {host}: {", ".join(missing)}')
    if busy:
        if not a.unload_first:
            raise SystemExit(f'Hay modelos cargados en {host}: {", ".join(busy)}. Usa --unload-first o `ollama stop <modelo>`.')
        unload_all(host)
    used = wait_gpu_free(host, GPU_BUSY_MIB)  # tras descargar, la memoria tarda unos segundos en liberarse
    if used is not None and used > GPU_BUSY_MIB and not a.allow_busy:
        raise SystemExit(f'La GPU está ocupada ({used} MiB en uso con el servidor vacío). Libérala o usa --allow-busy '
                         '(las mediciones de costo no serían válidas).')

    matrix_id = rx.utc_now().strftime('%Y%m%dT%H%M%SZ') + '_' + uuid.uuid4().hex[:6]
    runs_dir = pathlib.Path(a.runs_dir)
    passes = plan_passes(a.model_list, a.repeats, a.warmup, a.interleave)
    record = {'matrix_id': matrix_id, 'started_utc': rx.utc_now().isoformat(), 'finished_utc': None, 'status': 'interrupted',
              'models': a.model_list, 'host': host, 'split': a.split, 'prompt_version': a.prompt_version,
              'warmup': a.warmup, 'repeats': a.repeats, 'interleave': a.interleave, 'sequential': True,
              'data': a.data, 'data_sha256': rx.sha256_file(a.data), 'gpu_used_mib_at_start': used, 'passes': []}
    matrix_path = runs_dir / f'{matrix_id}.matrix.json'
    print(f'Matriz {matrix_id}: {len(passes)} pasada(s) en secuencia ({"intercalada" if a.interleave else "por bloques"}).')
    try:
        prev = None
        for ps in passes:
            safe = ''.join(c if c.isalnum() else '_' for c in ps['model'])
            suffix = f'rep{ps["rep_start"]}' if a.interleave else 'bloque'
            out = runs_dir / f'{matrix_id}_{safe}_{suffix}.jsonl'
            if not a.interleave and prev and prev != ps['model']:
                unload(host, prev)  # un solo modelo a la vez en los bloques
            argv_run = ['--model', ps['model'], '--host', host, '--data', a.data, '--config', a.config, '--split', a.split,
                        '--prompt-version', a.prompt_version, '--tasks', a.tasks, '--warmup', str(ps['warmup']), '--repeats', str(ps['repeats']),
                        '--rep-start', str(ps['rep_start']), '--matrix-id', matrix_id, '--output', str(out)]
            if a.limit:
                argv_run += ['--limit', str(a.limit)]
            try:
                code = rx.main(argv_run)
                msg = None
            except SystemExit as e:  # error de configuración del runner: se detiene toda la matriz
                code, msg = 2, str(e)
            record['passes'].append({**ps, 'output': str(out), 'output_name': out.name, 'exit_code': code, 'message': msg})
            if msg:
                raise SystemExit(f'La pasada de {ps["model"]} falló: {msg}')
            prev = ps['model']
        record['status'] = 'completed' if all(p['exit_code'] == 0 for p in record['passes']) else 'completed_with_errors'
    finally:
        record['finished_utc'] = rx.utc_now().isoformat()
        with rx.open_new(matrix_path) as f:
            json.dump(record, f, ensure_ascii=False, indent=2)
            f.write('\n')
        if not a.interleave:
            unload_all(host)

    outs = [p['output'] for p in record['passes']]
    print(f'\nMatriz {record["status"]}. Manifiesto: {matrix_path}')
    print('Para puntuar:  python src/score.py ' + ' '.join(f'--run "{o}"' for o in outs) + f' --dataset "{a.data}"')
    return 0 if record['status'] == 'completed' else 1


if __name__ == '__main__':
    sys.exit(main())
