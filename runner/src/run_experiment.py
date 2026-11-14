"""Ejecuta una corrida local contra Ollama y guarda resultados crudos (JSONL) + manifiesto (JSON).

v0.3: derivado del starter v0.1 (ver CHANGES.md). Solo biblioteca estandar.
Acepta el dataset antiguo (pilot_examples.jsonl) y el nuevo (dataset/data/items.jsonl).
Uso:
    python src/run_experiment.py --model qwen3:0.6b-q4_K_M --host http://127.0.0.1:11435 --limit 3
    python src/run_experiment.py --model qwen3:0.6b-q4_K_M --data ../dataset/data/items.jsonl --split dev \
        --prompt-version prompt-v0.3 --warmup 1 --repeats 3

Una corrida funcional NO es evidencia estadistica. Los pases de calentamiento se registran pero se marcan
(is_warmup=true) y el corrector los excluye.
"""
import argparse
import datetime as dt
import hashlib
import json
import os
import pathlib
import platform
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid

ROOT = pathlib.Path(__file__).resolve().parents[1]
DEFAULT_HOST = 'http://127.0.0.1:11434'
RUNNER_VERSION = 'runner-v0.3'
V03_FAMILY = ('prompt-v0.3', 'prompt-v0.4a', 'prompt-v0.4b', 'prompt-v0.4c',
              'prompt-v0.5a', 'prompt-v0.5b', 'prompt-v0.5c')
PROMPT_VERSIONS = ('prompt-v0.2',) + V03_FAMILY
TASKS_ALL = ('solve', 'diagnose', 'hint')
DEFAULT_PROMPT_VERSION = 'prompt-v0.2'  # compatible con la prueba de humo (Hito 1)
# Prompt CONGELADO para la evaluación (docs/prompt_tuning_dev_r2.md). No se modifica: cambiarlo tras ver resultados de
# `pilot` exige una versión nueva y reportar ambas. Una prueba verifica la huella de sus plantillas.
FROZEN_PROMPT_VERSION = 'prompt-v0.5b'
FROZEN_PROMPT_SHA256 = 'fc1af120764809200b53847ee0eafd837702a4c39bc4604fa7ab1648818a4b08'
SPLITS = ('all', 'dev', 'pilot', 'train', 'val', 'test')
GPU_ONLY_RATIO = 0.99  # fraccion minima del modelo en VRAM para llamarlo 'gpu_only'

# Solo el rol pedagogico. Sin metainstrucciones de investigacion (audit E-09).
SYSTEM = (
    'Responde en español claro y apropiado para un estudiante de tercer grado de primaria. '
    'No inventes datos. Lee con cuidado el enunciado.'
)

# Ignora proxies del sistema/entorno: el trafico es solo local (audit M-04).
_OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}))


def utc_now():
    return dt.datetime.now(dt.timezone.utc)


def normalize_host(host):
    host = (host or DEFAULT_HOST).strip()
    if '://' not in host:
        host = 'http://' + host
    return host.rstrip('/')


def is_loopback(host):
    name = urllib.parse.urlparse(host).hostname or ''
    return name in ('127.0.0.1', 'localhost', '::1')


def request_json(url, payload=None, timeout=240):
    data = json.dumps(payload, ensure_ascii=False).encode('utf-8') if payload is not None else None
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
    try:
        with _OPENER.open(req, timeout=timeout) as res:
            return json.load(res)
    except urllib.error.HTTPError as e:  # conserva el cuerpo del error de Ollama (audit M-03)
        body = e.read().decode('utf-8', 'replace')[:500]
        raise RuntimeError(f'HTTP {e.code}: {body}') from e


def sha256_file(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def sha256_text(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def open_new(path):
    """Abre un archivo NUEVO; falla si ya existe (nunca sobrescribe resultados crudos)."""
    path = pathlib.Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    return path.open('x', encoding='utf-8')


def solve_format_instruction(op, version):
    """Última frase del prompt de `solve`: cómo pedir la línea 'Respuesta final'. Es lo ÚNICO que difiere entre
    las variantes v0.3 / v0.4a / v0.4b / v0.4c (se ajusta por legibilidad del formato, nunca por exactitud)."""
    div = op == 'div'
    if version == 'prompt-v0.3':      # marcadores <número>
        fmt = 'cociente <número>, residuo <número>' if div else '<número>'
        return f'Termina con una última línea con este formato exacto: Respuesta final: {fmt}'
    if version == 'prompt-v0.4a':     # letras en vez de ángulos
        if div:
            return ('Termina con una última línea con este formato exacto: Respuesta final: cociente N, residuo M '
                    '(reemplaza N y M por los números, sin símbolos < >).')
        return 'Termina con una última línea con este formato exacto: Respuesta final: N (reemplaza N por el número).'
    if version == 'prompt-v0.4b':     # ejemplo con otros números
        if div:
            return 'Termina con una última línea con el formato del ejemplo (con otros números): Respuesta final: cociente 7, residuo 2'
        return 'Termina con una última línea con el formato del ejemplo (con otro número): Respuesta final: 123'
    if version == 'prompt-v0.4c':     # solo palabras, sin marcadores ni ejemplo
        if div:
            return ('Termina con una última línea que empiece con «Respuesta final:» y diga el cociente y el residuo '
                    'con esas palabras.')
        return 'Termina con una última línea que empiece con «Respuesta final:» seguida solo del resultado.'
    if version == 'prompt-v0.5c':     # v0.4a + aviso explícito contra copiar la indicación
        return solve_format_instruction(op, 'prompt-v0.4a') + ' No copies esta indicación.'
    raise ValueError('Versión de prompt desconocida: ' + str(version))


# Ejemplos de v0.5a: problemas AJENOS al dataset y a las sondas, con respuestas que no coinciden con ninguna de ellas.
_EXAMPLE_NUM = ('Ana tiene 12 lápices y compra 3 más. ¿Cuántos lápices tiene?', 'Respuesta final: 15')
_EXAMPLE_DIV = ('Se reparten 62 fichas por igual entre 8 niños. ¿Cuántas fichas recibe cada niño y cuántas sobran?',
                'Respuesta final: cociente 7, residuo 6')


def solve_prompt(base, op, version):
    """Prompt completo de `solve` para la familia v0.3+. Solo cambia dónde y cómo se pide la línea final."""
    head = 'Resuelve el siguiente problema y explica brevemente el procedimiento.'
    div = op == 'div'
    if version == 'prompt-v0.5a':     # ejemplo resuelto completo antes del problema
        ex_p, ex_a = _EXAMPLE_DIV if div else _EXAMPLE_NUM
        return (f'Ejemplo (otro problema, solo para mostrar el formato):\nProblema: {ex_p}\n{ex_a}\n\n'
                f'{head}\nProblema: {base}\nTermina con una última línea de la forma «Respuesta final: …» como en el ejemplo.')
    if version == 'prompt-v0.5b':     # la indicación de formato va ANTES del problema
        fmt = ('Escribe al final una línea que empiece con «Respuesta final:» y diga el cociente y el residuo con esas palabras.'
               if div else 'Escribe al final una línea que empiece con «Respuesta final:» seguida solo del número.')
        return f'{fmt}\n{head}\nProblema: {base}'
    return f'{head}\nProblema: {base}\n' + solve_format_instruction(op, version)


def prompt_for(ex, version=DEFAULT_PROMPT_VERSION):
    """Construye el prompt de usuario. v0.3 pide formatos estructurados para poder corregir de forma
    determinista y NO revela al modelo si la respuesta del estudiante tiene un error."""
    base = ex['problem']
    task = ex['task']
    if version == 'prompt-v0.2':
        if task == 'solve':
            return f'Resuelve el siguiente problema y explica brevemente el procedimiento.\nProblema: {base}'
        if task == 'diagnose':
            return (f'Problema: {base}\nRespuesta de un estudiante: {ex["student_answer"]}.\n'
                    'Indica si es correcta y explica el error específico que cometió, '
                    'sin inventar el razonamiento del estudiante.')
        if task == 'hint':
            return (f'Problema: {base}\nRespuesta de un estudiante: {ex["student_answer"]}.\n'
                    'Da una sola pista para que el estudiante descubra su error. No reveles el resultado final.')
        raise ValueError('Tarea desconocida: ' + str(task))
    if version in V03_FAMILY:
        if task == 'solve':
            return solve_prompt(base, ex.get('operation'), version)
        if task == 'diagnose':
            return (f'Problema: {base}\nRespuesta de un estudiante: {ex["student_answer"]}.\n'
                    'Empieza con una primera línea con este formato exacto: Veredicto: correcta '
                    '(o Veredicto: incorrecta). Después, si es incorrecta, explica el error específico que cometió, '
                    'sin inventar el razonamiento del estudiante.')
        if task == 'hint':
            return (f'Problema: {base}\nRespuesta de un estudiante: {ex["student_answer"]}.\n'
                    'Da una sola pista para que el estudiante revise su respuesta. No reveles el resultado final.')
        raise ValueError('Tarea desconocida: ' + str(task))
    raise ValueError('Versión de prompt desconocida: ' + str(version))


def load_dataset(path):
    """Carga el dataset antiguo (id/problem) o el nuevo (item_id/problem_text) y valida lo básico.
    Devuelve dicts con las claves que usa el runner (id, problem) más todos los campos originales."""
    rows = [json.loads(x) for x in pathlib.Path(path).read_text(encoding='utf-8').splitlines() if x.strip()]
    out, seen = [], set()
    for i, raw in enumerate(rows, 1):
        ex = dict(raw)
        if 'item_id' in ex:  # formato nuevo
            ex['id'] = ex['item_id']
            ex['problem'] = ex.get('problem_text')
        for key in ('id', 'task', 'topic', 'problem'):
            if not ex.get(key):
                raise ValueError(f'Item {i}: falta el campo obligatorio "{key}"')
        if ex['task'] not in ('solve', 'diagnose', 'hint'):
            raise ValueError(f'Item {ex["id"]}: tarea desconocida "{ex["task"]}"')
        if ex['task'] in ('diagnose', 'hint') and not ex.get('student_answer'):
            raise ValueError(f'Item {ex["id"]}: la tarea {ex["task"]} requiere student_answer')
        if ex['id'] in seen:
            raise ValueError(f'Id duplicado: {ex["id"]}')
        seen.add(ex['id'])
        out.append(ex)
    return out


def offload_mode(size, size_vram):
    """Clasifica el modo de ejecucion a partir de /api/ps (valores reportados por Ollama)."""
    if not size or size <= 0 or size_vram is None:
        return 'unknown'
    if size_vram <= 0:
        return 'cpu_only'
    if size_vram >= size * GPU_ONLY_RATIO:
        return 'gpu_only'
    return 'hybrid'


def is_truncated(result, num_predict):
    """Una respuesta esta truncada si Ollama dice 'length' o si agoto num_predict."""
    if result.get('done_reason') == 'length':
        return True
    n = result.get('eval_count')
    return n is not None and n >= num_predict


def ps_snapshot(host, model):
    """Estado del modelo cargado segun /api/ps. Devuelve None si no se puede consultar."""
    try:
        ps = request_json(host + '/api/ps', timeout=15)
    except (RuntimeError, OSError, ValueError):
        return None
    for m in ps.get('models', []):
        if m.get('name') == model or m.get('model') == model:
            return {
                'source': 'reported_by_ollama(/api/ps)',
                'size_bytes': m.get('size'), 'size_vram_bytes': m.get('size_vram'),
                'mode': offload_mode(m.get('size'), m.get('size_vram')),
                'gpu_only_threshold': GPU_ONLY_RATIO,
                'context_length': m.get('context_length'), 'runner': m.get('runner'),
                'digest': m.get('digest'),
            }
    return {'source': 'reported_by_ollama(/api/ps)', 'mode': 'unknown', 'note': 'modelo no aparece en /api/ps'}


def gpu_snapshot():
    """Lectura de nvidia-smi (medida externa). None si no esta disponible."""
    cmd = ['nvidia-smi', '--query-gpu=name,memory.total,memory.used,driver_version,temperature.gpu',
           '--format=csv,noheader,nounits']
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=10, check=True).stdout
    except (OSError, subprocess.SubprocessError):
        return None
    gpus = []
    for line in out.strip().splitlines():
        p = [x.strip() for x in line.split(',')]
        if len(p) == 5:
            gpus.append({'name': p[0], 'memory_total_mib': p[1], 'memory_used_mib': p[2],
                         'driver_version': p[3], 'temperature_c': p[4]})
    return {'source': 'measured_external(nvidia-smi)', 'taken_utc': utc_now().isoformat(), 'gpus': gpus}


def environment_info():
    return {'python': sys.version.split()[0], 'platform': platform.platform(), 'machine': platform.machine(),
            'processor': platform.processor(), 'cpu_count': os.cpu_count(), 'runner_version': RUNNER_VERSION}


def show_subset(host, model):
    """Detalles locales del modelo (/api/show). Si falla, devuelve el error en vez de ocultarlo."""
    try:
        s = request_json(host + '/api/show', {'model': model}, timeout=60)
    except (RuntimeError, OSError, ValueError) as e:
        return {'error': str(e)}
    ctx = next((v for k, v in (s.get('model_info') or {}).items() if k.endswith('.context_length')), None)
    return {'details': s.get('details'), 'parameters': s.get('parameters'),
            'capabilities': s.get('capabilities'), 'architecture_context_length': ctx,
            'template_sha256': sha256_text(s.get('template') or '')}


def parse_args(argv):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument('--model', required=True)
    p.add_argument('--host', default=os.environ.get('OLLAMA_HOST') or DEFAULT_HOST,
                   help='URL de Ollama (por defecto OLLAMA_HOST o http://127.0.0.1:11434)')
    p.add_argument('--limit', type=int, default=None)
    p.add_argument('--output', default=None, help='archivo .jsonl NUEVO (falla si existe)')
    p.add_argument('--data', default=str(ROOT / 'data' / 'pilot_examples.jsonl'))
    p.add_argument('--config', default=str(ROOT / 'configs' / 'experiment.json'))
    p.add_argument('--split', choices=SPLITS, default='all', help='filtra por partición (solo dataset nuevo)')
    p.add_argument('--prompt-version', choices=PROMPT_VERSIONS, default=DEFAULT_PROMPT_VERSION)
    p.add_argument('--tasks', default=','.join(TASKS_ALL), help='tareas a ejecutar, separadas por coma (solve,diagnose,hint)')
    p.add_argument('--warmup', type=int, default=0, help='pases COMPLETOS de calentamiento, descartados al corregir')
    p.add_argument('--repeats', type=int, default=1, help='pases medidos')
    p.add_argument('--rep-start', type=int, default=1, help='numero de la primera repeticion medida')
    p.add_argument('--matrix-id', default=None, help='identificador de la matriz de corridas (lo pone run_matrix.py)')
    p.add_argument('--allow-remote', action='store_true',
                   help='permite un host que no sea local (rompe el principio offline; no recomendado)')
    a = p.parse_args(argv)
    if a.warmup < 0 or a.repeats < 1 or a.rep_start < 1:
        p.error('--warmup >= 0, --repeats >= 1 y --rep-start >= 1')
    a.task_list = [t.strip() for t in a.tasks.split(',') if t.strip()]
    if not a.task_list or any(t not in TASKS_ALL for t in a.task_list):
        p.error('--tasks solo admite solve, diagnose y hint')
    return a


def main(argv=None):
    args = parse_args(sys.argv[1:] if argv is None else argv)
    host = normalize_host(args.host)
    if not is_loopback(host) and not args.allow_remote:
        raise SystemExit(f'Host no local ({host}). El experimento es offline; usa --allow-remote solo si lo decides.')

    conf_path, data_path = pathlib.Path(args.config), pathlib.Path(args.data)
    conf = json.loads(conf_path.read_text(encoding='utf-8'))
    dataset = load_dataset(data_path)
    n_dataset = len(dataset)
    if args.split != 'all':
        if not all('split' in ex for ex in dataset):
            raise SystemExit('--split solo aplica a un dataset con campo "split" (el dataset nuevo).')
        dataset = [ex for ex in dataset if ex['split'] == args.split]
        if not dataset:
            raise SystemExit(f'No hay ítems en la partición "{args.split}".')
    dataset = [ex for ex in dataset if ex['task'] in args.task_list]
    if args.limit is not None:
        dataset = dataset[:args.limit]

    try:
        version = request_json(host + '/api/version', timeout=15).get('version')
        tags = request_json(host + '/api/tags', timeout=30).get('models', [])
    except (urllib.error.URLError, TimeoutError, RuntimeError, OSError) as e:
        raise SystemExit(f'No se pudo conectar con Ollama en {host}. Comprueba que el servidor esté abierto. Detalle: {e}')
    matched = next((m for m in tags if m.get('name') == args.model or m.get('model') == args.model), None)
    if not matched:
        raise SystemExit(f'Modelo no instalado en {host}. Ejecuta: ollama pull {args.model}')
    digest = matched.get('digest')

    options = {k: conf[k] for k in ('temperature', 'seed', 'num_ctx', 'num_predict')}
    think = False if (conf.get('disable_thinking_for_qwen3') and args.model.startswith('qwen3:')) else None

    run_id = uuid.uuid4().hex[:8]
    started = utc_now()
    safe = ''.join(c if c.isalnum() else '_' for c in args.model)
    target = pathlib.Path(args.output) if args.output else ROOT / 'runs' / f'{started.strftime("%Y%m%dT%H%M%SZ")}_{safe}_{run_id}.jsonl'
    manifest_path = target.with_suffix('.manifest.json')
    if manifest_path.exists():
        raise SystemExit(f'Ya existe {manifest_path}; no se sobrescribe.')
    try:
        fout = open_new(target)
    except FileExistsError:
        raise SystemExit(f'Ya existe {target}; no se sobrescribe. Elige otro --output o no lo indiques.')

    manifest = {
        'manifest_version': 'manifest-v0.3', 'run_id': run_id, 'matrix_id': args.matrix_id, 'status': 'interrupted',
        'started_utc': started.isoformat(), 'finished_utc': None,
        'args': {'model': args.model, 'host': host, 'limit': args.limit, 'output': str(target), 'split': args.split,
                 'tasks': args.task_list},
        'environment': environment_info(), 'gpu_before': gpu_snapshot(),
        'ollama': {'version': version, 'model_tag': args.model, 'model_digest': digest,
                   'show': show_subset(host, args.model)},
        'dataset': {'path': str(data_path), 'sha256': sha256_file(data_path),
                    'n_items_in_file': n_dataset, 'n_items_run': len(dataset), 'split_filter': args.split},
        'config': {'path': str(conf_path), 'sha256': sha256_file(conf_path), 'content': conf,
                   'effective_options': options, 'think': think},
        'prompt': {'version': args.prompt_version, 'system': SYSTEM, 'system_sha256': sha256_text(SYSTEM)},
        'passes': {'warmup': args.warmup, 'repeats': args.repeats, 'rep_start': args.rep_start},
        'offload_first': None, 'offload_last': None, 'gpu_after': None,
        'counts': {'items': 0, 'errors': 0, 'truncated': 0},
        'measured': {'items': 0, 'errors': 0, 'truncated': 0},
        'provenance': {
            'reported_by_ollama': ['total_duration', 'load_duration', 'prompt_eval_count', 'prompt_eval_duration',
                                   'eval_count', 'eval_duration', 'done_reason', 'offload (/api/ps)'],
            'measured_external': ['gpu_before/gpu_after (nvidia-smi)', 'wall_seconds (reloj del script)'],
        },
        'network_check': 'no realizado por el runner (el modo sin red se comprueba aparte)',
        'limitations': ['Las duraciones son estadísticas de Ollama, no mediciones de RAM, VRAM ni energía.',
                        'counts incluye los pases de calentamiento; measured solo los pases medidos.'],
    }

    total_passes = args.warmup + args.repeats
    print(f'Ejecutando {len(dataset)} ítems x {total_passes} pase(s) ({args.warmup} de calentamiento) con '
          f'{args.model} en {host}; archivo: {target}')
    try:
        for pass_idx in range(total_passes):
            is_warmup = pass_idx < args.warmup
            rep = 0 if is_warmup else args.rep_start + (pass_idx - args.warmup)
            for ex in dataset:
                prompt = prompt_for(ex, args.prompt_version)
                body = {
                    'model': args.model, 'stream': False,
                    'messages': [{'role': 'system', 'content': SYSTEM}, {'role': 'user', 'content': prompt}],
                    'options': options, 'keep_alive': '5m',
                }
                if think is not None:
                    body['think'] = think
                started_item = time.perf_counter()
                try:
                    result = request_json(host + '/api/chat', body)
                except (RuntimeError, OSError, ValueError) as e:  # urllib.error.URLError es OSError
                    result = {'error': f'{type(e).__name__}: {e}'}
                wall_s = time.perf_counter() - started_item
                message = result.get('message') or {}
                record = {
                    'run_id': run_id, 'matrix_id': args.matrix_id, 'id': ex['id'], 'item_id': ex.get('item_id', ex['id']),
                    'problem_base_id': ex.get('problem_base_id'), 'split': ex.get('split'),
                    'task': ex['task'], 'topic': ex['topic'], 'operation': ex.get('operation'),
                    'rep': rep, 'is_warmup': is_warmup,
                    'model': args.model, 'model_digest': digest, 'protocol': conf['protocol_version'],
                    'prompt_version': args.prompt_version, 'prompt': prompt,
                    'prompt_sha256': sha256_text(SYSTEM + '\n' + prompt), 'system': SYSTEM,
                    'generation_settings': options, 'think': body.get('think'),
                    'created_utc': utc_now().isoformat(),
                    'response': message.get('content', ''), 'reasoning': message.get('thinking'),
                    'done_reason': result.get('done_reason'),
                    'truncated': is_truncated(result, options['num_predict']) if not result.get('error') else None,
                    'wall_seconds': round(wall_s, 4),
                    'total_duration_ns': result.get('total_duration'), 'load_duration_ns': result.get('load_duration'),
                    'prompt_eval_count': result.get('prompt_eval_count'),
                    'prompt_eval_duration_ns': result.get('prompt_eval_duration'),
                    'eval_count': result.get('eval_count'), 'eval_duration_ns': result.get('eval_duration'),
                    'error': result.get('error'),
                    'gold_answer': ex.get('gold_answer'), 'gold_error': ex.get('gold_error'),
                    'student_answer': ex.get('student_answer'),
                    'student_answer_is_correct': ex.get('student_answer_is_correct'),
                    'source_reference': ex.get('source_reference') or ex.get('curriculum_page'),
                }
                fout.write(json.dumps(record, ensure_ascii=False) + '\n')
                fout.flush()
                for key in (('counts',) if is_warmup else ('counts', 'measured')):
                    manifest[key]['items'] += 1
                    manifest[key]['errors'] += 1 if record['error'] else 0
                    manifest[key]['truncated'] += 1 if record['truncated'] else 0
                if manifest['offload_first'] is None and not record['error']:
                    manifest['offload_first'] = ps_snapshot(host, args.model)
                tag = 'ERROR: ' + record['error'] if record['error'] else ('OK (truncada)' if record['truncated'] else 'OK')
                print(('[calentamiento] ' if is_warmup else f'[rep {rep}] ') + ex['id'], tag)
        manifest['status'] = 'completed'
    finally:
        fout.close()
        manifest['offload_last'] = ps_snapshot(host, args.model)
        manifest['gpu_after'] = gpu_snapshot()
        manifest['finished_utc'] = utc_now().isoformat()
        with open_new(manifest_path) as fm:
            json.dump(manifest, fm, ensure_ascii=False, indent=2)
            fm.write('\n')

    c = manifest['counts']
    mode = (manifest['offload_first'] or {}).get('mode', 'desconocido')
    print(f'Listo. ítems={c["items"]} errores={c["errors"]} truncadas={c["truncated"]} modo={mode}. Manifiesto: {manifest_path}')
    print('Las respuestas aún requieren evaluación humana y verificación matemática.')
    return 1 if c['errors'] else 0


if __name__ == '__main__':
    sys.exit(main())
