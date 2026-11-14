"""Mide la capacidad de la GPU para los modelos del proyecto y guarda los DATOS CRUDOS con su procedencia.

Tres mediciones, solo local (servidor de Ollama en 127.0.0.1:11435), secuenciales:
  1) Huella de cada modelo con las opciones del runner (num_ctx 2048): memoria que reporta Ollama (/api/ps) y la subida de memoria
     de la GPU medida con nvidia-smi.
  2) Co-carga: cuántos modelos mantiene cargados a la vez el servidor (de menor a mayor huella).
  3) Concurrencia: tokens/s de tres precisiones de Qwen3-0.6B en solitario frente a ejecutadas a la vez.
Exploratorio (pocas repeticiones). NO usar con otra cosa corriendo en el equipo: la medición 3 es sensible a la carga.

Uso:  python tools/gpu_capacity.py --out results/gpu_capacity/gpu_capacity_20261114.json
"""
import argparse
import datetime as dt
import json
import pathlib
import statistics as st
import subprocess
import sys
import threading
import time
import urllib.request

HOST = 'http://127.0.0.1:11435'
OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}))
OPTS = {'num_ctx': 2048, 'num_predict': 200, 'temperature': 0, 'seed': 42}
PROMPT = 'Explica paso a paso y con mucho detalle cómo se resuelve la resta 725 − 348 para un niño de tercer grado.'
MODELS = ['qwen3:0.6b-q4_K_M', 'qwen3:0.6b-q8_0', 'qwen3:0.6b-fp16', 'qwen3:1.7b-q4_K_M', 'qwen3:1.7b-q8_0',
          'qwen3:1.7b-fp16', 'qwen3:4b-q4_K_M', 'gemma3:270m-it-q8_0', 'gemma3:1b-it-q4_K_M', 'llama3.2:1b-instruct-q4_K_M',
          'deepseek-r1:1.5b-qwen-distill-q4_K_M', 'phi4-mini:3.8b-q4_K_M', 'hf.co/ggml-org/SmolLM3-3B-GGUF:Q4_K_M']
CO_LOAD_ORDER = ['gemma3:270m-it-q8_0', 'qwen3:0.6b-q4_K_M', 'gemma3:1b-it-q4_K_M', 'llama3.2:1b-instruct-q4_K_M',
                 'qwen3:0.6b-q8_0', 'deepseek-r1:1.5b-qwen-distill-q4_K_M']
TRIO = ['qwen3:0.6b-q4_K_M', 'qwen3:0.6b-q8_0', 'qwen3:0.6b-fp16']


def call(path, payload=None, timeout=600):
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(HOST + path, data=data, headers={'Content-Type': 'application/json'})
    with OPENER.open(req, timeout=timeout) as r:
        return json.load(r)


def gpu():
    out = subprocess.run(['nvidia-smi', '--query-gpu=name,memory.used,memory.total,temperature.gpu,driver_version',
                          '--format=csv,noheader,nounits'], capture_output=True, text=True, timeout=10).stdout.strip().split(',')
    return {'name': out[0].strip(), 'used_mib': int(out[1]), 'total_mib': int(out[2]), 'temp_c': int(out[3]), 'driver': out[4].strip()}


def unload_all():
    for x in call('/api/ps')['models']:
        try:
            call('/api/generate', {'model': x['name'], 'keep_alive': 0}, timeout=60)
        except Exception:
            pass
    for _ in range(30):
        if not call('/api/ps')['models']:
            return
        time.sleep(1.5)


def wait_gpu(limit):
    for _ in range(30):
        if gpu()['used_mib'] <= limit:
            return
        time.sleep(1.5)


def gen(model, n=None):
    o = dict(OPTS)
    if n:
        o['num_predict'] = n
    body = {'model': model, 'prompt': PROMPT, 'stream': False, 'keep_alive': '120s', 'options': o}
    if model.startswith('qwen3:'):
        body['think'] = False
    r = call('/api/generate', body)
    return r['eval_count'] / (r['eval_duration'] / 1e9) if r.get('eval_duration') else None


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument('--out', required=True)
    a = p.parse_args()
    out = pathlib.Path(a.out)
    if out.exists():
        raise SystemExit(f'Ya existe {out}; no se sobrescribe.')
    assert not call('/api/ps')['models'], 'hay modelos cargados en el servidor'
    base = gpu()
    assert base['used_mib'] < 1500, f'GPU ocupada ({base["used_mib"]} MiB)'
    tags = {m['name']: m['digest'] for m in call('/api/tags')['models']}
    res = {'meta': {'started_utc': dt.datetime.now(dt.timezone.utc).isoformat(), 'ollama_version': call('/api/version')['version'],
                    'gpu': base, 'host': 'local (127.0.0.1)', 'server_default_note': 'Ollama sin cambios de OLLAMA_MAX_LOADED_MODELS',
                    'digests': {m: tags.get(m) for m in MODELS},
                    'provenance': {'ollama': ['size, size_vram (/api/ps)', 'eval_count, eval_duration (/api/generate)'],
                                   'nvidia-smi': ['memory.used', 'temperature.gpu']},
                    'limitations': ['Exploratorio: pocas repeticiones, un solo equipo (portátil).',
                                    'La concurrencia se midió con 3 solicitudes simultáneas del mismo prompt.']}}
    # 1) Huella por modelo
    foot = []
    for m in MODELS:
        t0 = time.time()
        try:
            r = call('/api/generate', {'model': m, 'prompt': 'Hola', 'stream': False, 'keep_alive': '90s',
                                       'options': {'num_ctx': 2048, 'num_predict': 1, 'temperature': 0, 'seed': 42}})
            e = next((x for x in call('/api/ps')['models'] if x['name'] == m), {})
            g = gpu()
            foot.append({'model': m, 'ok': True, 'size_mib': round(e.get('size', 0) / 2**20), 'size_vram_mib': round(e.get('size_vram', 0) / 2**20),
                         'context_length': e.get('context_length'), 'gpu_used_mib': g['used_mib'], 'gpu_delta_mib': g['used_mib'] - base['used_mib'],
                         'load_s': round((r.get('load_duration') or 0) / 1e9, 2), 'wall_s': round(time.time() - t0, 1), 'temp_c': g['temp_c']})
        except Exception as ex:
            foot.append({'model': m, 'ok': False, 'error': str(ex)[:150]})
        unload_all()
        wait_gpu(base['used_mib'] + 400)
    res['footprint'] = foot
    # 2) Co-carga
    co = []
    for i, m in enumerate(CO_LOAD_ORDER, 1):
        gen(m, 1)
        ps = call('/api/ps')['models']
        co.append({'loading': m, 'loaded_now': len(ps), 'loaded_names': [x['name'] for x in ps],
                   'modes': ['gpu' if x['size_vram'] >= 0.99 * x['size'] else 'hybrid' for x in ps], 'gpu_used_mib': gpu()['used_mib']})
        if len(ps) < i:
            break
    res['co_load'] = co
    unload_all()
    wait_gpu(base['used_mib'] + 400)
    # 3) Concurrencia
    solo = {m: [] for m in TRIO}
    for m in TRIO:
        gen(m, 5)
        for _ in range(3):
            solo[m].append(gen(m))
    unload_all()
    for m in TRIO:
        gen(m, 5)
    conc = {m: [] for m in TRIO}
    for _ in range(3):
        got = {}
        ths = [threading.Thread(target=lambda mm=m: got.__setitem__(mm, gen(mm))) for m in TRIO]
        [t.start() for t in ths]
        [t.join() for t in ths]
        for m in TRIO:
            conc[m].append(got[m])
    res['concurrency'] = {'prompt': PROMPT, 'num_predict': OPTS['num_predict'], 'solo_tokens_per_s': {m: [round(x, 1) for x in v] for m, v in solo.items()},
                          'concurrent_tokens_per_s': {m: [round(x, 1) for x in v] for m, v in conc.items()},
                          'median_solo': {m: round(st.median(v), 1) for m, v in solo.items()},
                          'median_concurrent': {m: round(st.median(v), 1) for m, v in conc.items()},
                          'models_loaded_during_concurrency': len(call('/api/ps')['models'])}
    unload_all()
    wait_gpu(base['used_mib'] + 400)
    res['meta']['finished_utc'] = dt.datetime.now(dt.timezone.utc).isoformat()
    res['meta']['gpu_end'] = gpu()
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open('x', encoding='utf-8') as f:
        json.dump(res, f, ensure_ascii=False, indent=2)
        f.write('\n')
    print('listo ->', out.name)
    return 0


if __name__ == '__main__':
    sys.exit(main())
