"""Genera los datos del sitio (assets/data/*.js) a partir de los archivos reales del proyecto.

Ninguna cifra del sitio se escribe a mano: salen de dataset/data/items.jsonl y de runner/runs/*.
Uso (desde la raíz del repo):  python tools/build_site_data.py
Regenera siempre assets/data/ (son artefactos derivados, se pueden sobrescribir).
"""
import datetime as dt
import hashlib
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
ITEMS = ROOT / 'dataset' / 'data' / 'items.jsonl'
RUNS = ROOT / 'runner' / 'runs'
OUT = ROOT / 'assets' / 'data'

ITEM_FIELDS = ['item_id', 'problem_base_id', 'competency_id', 'topic', 'task', 'difficulty', 'split',
               'problem_text', 'student_answer', 'gold_answer', 'gold_error_observable', 'gold_error_type',
               'error_generator', 'student_answer_is_correct', 'curriculum_page', 'reviewer_status']


def read_jsonl(path):
    return [json.loads(x) for x in pathlib.Path(path).read_text(encoding='utf-8-sig').splitlines() if x.strip()]


def sha16(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()[:16]


def js(name, obj):
    OUT.mkdir(parents=True, exist_ok=True)
    text = f'/* Generado por tools/build_site_data.py. No editar a mano. */\nwindow.{name} = ' \
           + json.dumps(obj, ensure_ascii=False, indent=1) + ';\n'
    (OUT / f'{name.lower()}.js').write_text(text, encoding='utf-8')


def build_items():
    items = read_jsonl(ITEMS)
    js('PROJECT_ITEMS', {'sha256_16': sha16(ITEMS), 'items': [{k: it[k] for k in ITEM_FIELDS} for it in items]})
    return items


def contains_gold(item, response):
    """Detección de fuga SOLO para hint: ¿aparece algún número de la respuesta correcta en la pista?"""
    if item['task'] != 'hint':
        return None
    gold_nums = {n for n in re.findall(r'\d+', item['gold_answer'])}
    return bool(gold_nums & set(re.findall(r'\d+', response)))


def build_runs():
    nets = sorted(RUNS.glob('*_network_state.json'))
    net_evidence = []
    for p in nets:
        e = json.loads(p.read_text(encoding='utf-8-sig'))
        net_evidence.append({'file': p.name, 'sha256_16': sha16(p), 'model': e.get('model'),
                             'offline_before': e.get('offline_before'), 'offline_after': e.get('offline_after'),
                             'runner_exit_code': e.get('runner_exit_code'),
                             'taken_before': e['before']['taken_utc'], 'taken_after': e['after']['taken_utc'],
                             'wifi_before': [a['status'] for a in e['before']['adapters'] if a['name'] == 'Wi-Fi'],
                             'wifi_after': [a['status'] for a in e['after']['adapters'] if a['name'] == 'Wi-Fi'],
                             'probe_before': [e['before']['probe_1_1_1_1_443'], e['before']['probe_8_8_8_8_53']],
                             'probe_after': [e['after']['probe_1_1_1_1_443'], e['after']['probe_8_8_8_8_53']]})
    runs = []
    for jp in sorted(RUNS.glob('*.jsonl')):
        if jp.name.endswith('.scores.jsonl'):
            continue
        mp = jp.with_suffix('.manifest.json')
        if not mp.exists():
            continue
        m = json.loads(mp.read_text(encoding='utf-8-sig'))
        if m.get('manifest_version') != 'manifest-v0.2':  # solo la prueba de humo (runner v0.2); las matrices son v0.3
            continue
        recs = read_jsonl(jp)
        # Corrida "sin red" = su inicio cae entre las dos lecturas de red del script y ambas dieron sin internet.
        # Se comparan las marcas ISO hasta el segundo (los formatos de 'Z' y '+00:00' difieren al final).
        offline = any(n['offline_before'] and n['offline_after']
                      and n['taken_before'][:19] <= m['started_utc'][:19] <= n['taken_after'][:19]
                      for n in net_evidence)
        g0, g1 = (m['gpu_before'] or {}).get('gpus', [{}])[0], (m['gpu_after'] or {}).get('gpus', [{}])[0]
        runs.append({
            'run_id': m['run_id'], 'file': jp.name, 'sha256_16': sha16(jp), 'manifest_sha256_16': sha16(mp),
            'started_utc': m['started_utc'], 'finished_utc': m['finished_utc'], 'status': m['status'],
            'items': len(recs), 'counts': m['counts'], 'offline_verified': offline,
            'model': m['args']['model'], 'digest': m['ollama']['model_digest'], 'ollama_version': m['ollama']['version'],
            'quantization': (m['ollama']['show'].get('details') or {}).get('quantization_level'),
            'offload_first': (m['offload_first'] or {}).get('mode'), 'offload_last': (m['offload_last'] or {}).get('mode'),
            'vram_bytes': (m['offload_first'] or {}).get('size_vram_bytes'),
            'gpu': {'name': g0.get('name'), 'mem_used_before_mib': g0.get('memory_used_mib'),
                    'mem_used_after_mib': g1.get('memory_used_mib'), 'temp_before_c': g0.get('temperature_c'),
                    'temp_after_c': g1.get('temperature_c')},
            'options': m['config']['effective_options'], 'think': m['config']['think'],
            'prompt_version': m['prompt']['version'], 'runner_version': m['environment']['runner_version'],
            'dataset_sha256_16': m['dataset']['sha256'][:16],
            'results': [{
                'id': r['id'], 'task': r['task'], 'student_answer': r['student_answer'], 'gold_answer': r['gold_answer'],
                'response': r['response'], 'wall_s': r['wall_seconds'], 'eval_count': r['eval_count'],
                'load_ms': round((r['load_duration_ns'] or 0) / 1e6), 'prompt_eval_ms': round((r['prompt_eval_duration_ns'] or 0) / 1e6),
                'done_reason': r['done_reason'], 'truncated': r['truncated'], 'has_reasoning': bool(r['reasoning']),
                'think_tag_in_response': '<think>' in r['response'], 'latex': '$' in r['response'],
                'hint_contains_gold': contains_gold(r, r['response'])} for r in recs],
        })
    runs.sort(key=lambda r: r['started_utc'])
    # Comparación de respuestas idénticas entre pares de corridas (solo ítems comunes)
    cmp = []
    for i in range(len(runs)):
        for j in range(i + 1, len(runs)):
            a = {r['id']: r['response'] for r in read_jsonl(RUNS / runs[i]['file'])}
            b = {r['id']: r['response'] for r in read_jsonl(RUNS / runs[j]['file'])}
            common = [k for k in a if k in b]
            same = [k for k in common if a[k] == b[k]]
            cmp.append({'a': runs[i]['run_id'], 'b': runs[j]['run_id'], 'common': len(common), 'identical': len(same),
                        'different_ids': [k for k in common if k not in same]})
    js('PROJECT_RUNS', {'runs': runs, 'network_evidence': net_evidence, 'comparisons': cmp})
    return runs


RESULTS = ROOT / 'results'


def load_json(path):
    return json.loads(pathlib.Path(path).read_text(encoding='utf-8-sig'))


def short_model(m):
    return m.split(':', 1)[1].replace('0.6b-', '')


def build_tests():
    """Datos de las páginas de pruebas, leídos de results/ (evidencia publicable) y del código congelado."""
    sys.path.insert(0, str(ROOT / 'runner' / 'src'))
    import run_experiment as rx

    sample = '«enunciado del problema»'

    def solve_texts(v):
        return {'sub': rx.prompt_for({'task': 'solve', 'problem': sample, 'operation': 'sub'}, v),
                'div': rx.prompt_for({'task': 'solve', 'problem': sample, 'operation': 'div'}, v)}

    gpu = load_json(sorted((RESULTS / 'gpu_capacity').glob('*.json'))[-1])
    rounds = []
    for rnd, folder, probes in ((1, 'format_tuning_r1', 'format_probes.jsonl'), (2, 'format_tuning_r2', 'format_probes_r2.jsonl')):
        dec = load_json(next((RESULTS / folder).glob('format_tuning_decision*.json')))
        pp = ROOT / 'dataset' / 'data' / probes
        prs = read_jsonl(pp)
        rounds.append({'round': rnd, 'decision': dec, 'matrices': len(list((RESULTS / folder).glob('*.matrix.json'))),
                       'probes_sha': hashlib.sha256(pp.read_bytes()).hexdigest(), 'probes_items': len(prs),
                       'probes_bases': len({p['problem_base_id'] for p in prs}),
                       'prompts': {v: solve_texts(v) for v in dec['variants']}})
    frozen = {'version': rx.FROZEN_PROMPT_VERSION, 'sha256': rx.FROZEN_PROMPT_SHA256, 'texts': {
        'solve_sub': solve_texts(rx.FROZEN_PROMPT_VERSION)['sub'], 'solve_div': solve_texts(rx.FROZEN_PROMPT_VERSION)['div'],
        'diagnose': rx.prompt_for({'task': 'diagnose', 'problem': sample, 'student_answer': '«respuesta del estudiante»'}, rx.FROZEN_PROMPT_VERSION),
        'hint': rx.prompt_for({'task': 'hint', 'problem': sample, 'student_answer': '«respuesta del estudiante»'}, rx.FROZEN_PROMPT_VERSION),
        'system': rx.SYSTEM}}

    pdir = RESULTS / 'pilot_qwen3_0.6b'
    matrix = load_json(next(pdir.glob('*.matrix.json')))
    report = load_json(next(pdir.glob('*.report.json')))
    scores = read_jsonl(next(pdir.glob('*.scores.jsonl')))
    mans = [load_json(p) for p in sorted(pdir.glob('*_rep*.manifest.json'))]
    total = sum(m['counts']['items'] for m in mans)
    measured = sum(m['measured']['items'] for m in mans)
    t0, t1 = (dt.datetime.fromisoformat(matrix[k]) for k in ('started_utc', 'finished_utc'))
    models = sorted({(m['ollama']['model_tag'], m['ollama']['model_digest'][:12], m['offload_first']['mode'],
                      (m['ollama']['show'].get('details') or {}).get('quantization_level')) for m in mans})
    pilot = {
        'matrix': {'id': matrix['matrix_id'], 'started_utc': matrix['started_utc'], 'finished_utc': matrix['finished_utc'],
                   'status': matrix['status'], 'prompt_version': matrix['prompt_version'], 'split': matrix['split'],
                   'interleave': matrix['interleave'], 'sequential': matrix['sequential'], 'warmup': matrix['warmup'], 'repeats': matrix['repeats']},
        'totals': {'records': total, 'measured': measured, 'warmup': total - measured,
                   'errors': sum(m['counts']['errors'] for m in mans), 'truncated': sum(m['counts']['truncated'] for m in mans)},
        'duration_s': (t1 - t0).total_seconds(),
        'models': [{'tag': a, 'digest': b, 'offload': c, 'quantization': d} for a, b, c, d in models],
        'report': report,
        'records': [{'i': r['item_id'], 'm': short_model(r['model']), 'r': r['rep'], 't': r['task'], 's': r['subgroup'], 'sc': r['score'],
                     'me': r['method'], 'd': r['detail'], 're': r['response'], 'w': r['wall_seconds'], 'ec': r['eval_count'],
                     'fl': {'latex': r['latex'], 'truncated': r['truncated'], 'think_leak': r['think_leak']}}
                    for r in scores if not r['is_warmup']]}
    return {'gpu': gpu, 'format': {'rounds': rounds, 'frozen': frozen}, 'pilot': pilot}


def main():
    items = build_items()
    runs = build_runs()
    js('PROJECT_TESTS', build_tests())
    print(f'items: {len(items)} | corridas de humo: {len(runs)} | pruebas: gpu, formato (2 rondas), piloto -> {OUT}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
