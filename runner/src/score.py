"""Corrector automático DETERMINISTA (v0.3). Solo biblioteca estándar.

Qué puntúa (y qué NO):
  solve    -> exactitud de la respuesta final (extraída con reglas explícitas) frente a la respuesta calculada.
  diagnose -> si el veredicto (correcta/incorrecta) coincide con la verdad. Mide sensibilidad (ítems con error)
              y especificidad (controles con respuesta correcta). NO puntúa si localizó bien el error.
  hint     -> si la pista contiene el resultado correcto (fuga). NO puntúa utilidad, claridad ni progresión.
La calidad pedagógica (localización del error, utilidad de la pista, edad) requiere rúbrica y revisión humana: pendiente.
Lo que no se puede leer se marca 'sin extracción' y NO se cuenta como acierto ni como fallo.

Uso:
  python src/score.py --run runs/A.jsonl [--run runs/B.jsonl ...] --dataset ../dataset/data/items.jsonl
"""
import argparse
import collections
import json
import math
import pathlib
import re
import sys
import unicodedata

NUM = re.compile(r'\d{1,3}(?:[   .,]\d{3})+(?!\d)|\d+')
FINAL = re.compile(r'respuesta\s+final\s*:\s*(.+)', re.I)
VERDICT = re.compile(r'veredicto\s*:\s*(incorrect[oa]|correct[oa])', re.I)
_BAD = re.compile(r'\b(?:es|esta|resulta)\s+(?:incorrect[oa]|mal|equivocad[oa]|erronead?[oa])\b|\bno\s+es\s+correct[oa]\b|\bno\s+esta\s+bien\b')
_GOOD = re.compile(r'\b(?:es|esta|resulta)\s+(?:correct[oa]|acertad[oa])\b|\besta\s+bien\b')


def norm(text):
    t = unicodedata.normalize('NFD', text or '')
    return ''.join(c for c in t if unicodedata.category(c) != 'Mn').lower()


def to_int(tok):
    return int(re.sub(r'[   .,]', '', tok))


def ints(text):
    return [to_int(m.group()) for m in NUM.finditer(text or '')]


def parse_div(text):
    t = norm(text)
    qm = re.search(r'cociente\D{0,20}?(\d+(?:[ .,]\d{3})*)', t)
    rm = re.search(r'(?:residuo|sobran?|resto)\D{0,20}?(\d+(?:[ .,]\d{3})*)', t)
    q = to_int(qm.group(1)) if qm else None
    if rm:
        r = to_int(rm.group(1))
    elif re.search(r'no\s+sobra|sin\s+residuo|residuo\s+(?:es\s+)?(?:cero|nulo)', t):
        r = 0
    else:
        r = None
    return {'quotient': q, 'remainder': r} if q is not None and r is not None else None


def parse_value(line):
    """Valor numérico de una línea: si hay '=', el primer número después del último '='; si no, el primero."""
    seg = line.rsplit('=', 1)[1] if '=' in line else line
    nums = ints(seg)
    return {'value': nums[0]} if nums else None


def extract_solve(response, op):
    """Devuelve (estructura|None, método): 'final_line' | 'fallback' | 'none'."""
    finals = list(FINAL.finditer(response or ''))
    if finals:
        line = finals[-1].group(1)
        got = parse_div(line) if op == 'div' else parse_value(line)
        if got is not None:
            return got, 'final_line'
    if op == 'div':
        got = parse_div(response)
        return (got, 'fallback') if got else (None, 'none')
    text = response or ''
    if '=' in text:
        nums = ints(text.rsplit('=', 1)[1])
        if nums:
            return {'value': nums[0]}, 'fallback'
    nums = ints(text)
    return ({'value': nums[-1]}, 'fallback') if nums else (None, 'none')


def extract_verdict(response):
    """Devuelve ('correcta'|'incorrecta'|None, método): 'verdict_line' | 'fallback' | 'none'."""
    t = norm(response)
    m = VERDICT.search(t)
    if m:
        return ('incorrecta' if m.group(1).startswith('incorrect') else 'correcta'), 'verdict_line'
    head = t[:300]
    bad = bool(_BAD.search(head))
    good = bool(_GOOD.search(_BAD.sub(' ', head)))  # "no es correcta" cuenta como incorrecta, no como ambas
    if bad and not good:
        return 'incorrecta', 'fallback'
    if good and not bad:
        return 'correcta', 'fallback'
    return None, 'none'


def gold_leak_values(item):
    g = item['gold_answer_struct']
    return [g['value']] if 'value' in g else [g['quotient']]


def score_record(rec, item):
    """Puntuación primaria de un registro. score: 1, 0 o None (sin extracción / error)."""
    task = rec['task']
    resp = rec.get('response') or ''
    out = {'score_name': None, 'score': None, 'method': None, 'detail': None}
    flags = {'latex': '$' in resp or '\\times' in resp or '\\frac' in resp, 'truncated': bool(rec.get('truncated')),
             'empty': not resp.strip(), 'think_leak': bool(rec.get('reasoning')) or '<think>' in resp}
    if rec.get('error'):
        out.update(score_name={'solve': 'solve_correct', 'diagnose': 'diagnose_verdict_correct', 'hint': 'hint_no_leak'}[task],
                   detail='error de ejecución')
        return {**out, **flags}
    if task == 'solve':
        got, method = extract_solve(resp, item['operation'])
        out.update(score_name='solve_correct', method=method, detail=got)
        if got is not None:
            out['score'] = 1 if got == item['gold_answer_struct'] else 0
    elif task == 'diagnose':
        verdict, method = extract_verdict(resp)
        expected = 'correcta' if item['student_answer_is_correct'] else 'incorrecta'
        out.update(score_name='diagnose_verdict_correct', method=method, detail={'verdict': verdict, 'expected': expected})
        if verdict is not None:
            out['score'] = 1 if verdict == expected else 0
    else:  # hint
        leaked = [v for v in gold_leak_values(item) if v in ints(resp)]
        out.update(score_name='hint_no_leak', method='numbers', detail={'leaked': leaked})
        out['score'] = 0 if leaked else 1
    return {**out, **flags}


def wilson(k, n, z=1.96):
    if n == 0:
        return None, None
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return max(0.0, (c - h) / d), min(1.0, (c + h) / d)


def load_jsonl(path):
    return [json.loads(x) for x in pathlib.Path(path).read_text(encoding='utf-8').splitlines() if x.strip()]


def sha256_file(path):
    import hashlib
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def score_runs(run_paths, dataset_path, allow_mismatch=False):
    """Puntúa todos los registros de las corridas. Devuelve (lista de registros puntuados, avisos)."""
    items = {i['item_id']: i for i in load_jsonl(dataset_path)}
    ds_sha = sha256_file(dataset_path)
    scored, warnings = [], []
    for rp in run_paths:
        rp = pathlib.Path(rp)
        mp = rp.with_suffix('.manifest.json')
        if mp.exists():
            m = json.loads(mp.read_text(encoding='utf-8-sig'))
            if m['dataset']['sha256'] != ds_sha and not allow_mismatch:
                raise SystemExit(f'{rp.name}: el dataset de la corrida no coincide con --dataset (SHA-256 distinto). '
                                 'Usa el dataset con el que se corrió, o --allow-dataset-mismatch bajo tu responsabilidad.')
        else:
            warnings.append(f'{rp.name}: sin manifiesto; no se pudo verificar el dataset')
        for rec in load_jsonl(rp):
            iid = rec.get('item_id') or rec['id']
            if iid not in items:
                raise SystemExit(f'{rp.name}: el ítem {iid} no existe en el dataset (¿corrida con el dataset antiguo?)')
            it = items[iid]
            s = score_record(rec, it)
            scored.append({
                'run_id': rec['run_id'], 'matrix_id': rec.get('matrix_id'), 'item_id': iid, 'problem_base_id': it['problem_base_id'],
                'split': it['split'], 'task': rec['task'], 'model': rec['model'], 'model_digest': rec['model_digest'],
                'prompt_version': rec['prompt_version'], 'rep': rec.get('rep', 1), 'is_warmup': rec.get('is_warmup', False),
                'subgroup': ('con_error' if it['student_answer_is_correct'] is False else 'control')
                if rec['task'] == 'diagnose' else 'todos',
                'wall_seconds': rec.get('wall_seconds'), 'eval_count': rec.get('eval_count'),
                'eval_duration_ns': rec.get('eval_duration_ns'), 'load_duration_ns': rec.get('load_duration_ns'),
                'response': rec.get('response'), **s})
    return scored, warnings


def summarize(scored):
    meas = [r for r in scored if not r['is_warmup']]
    groups = collections.defaultdict(list)
    for r in meas:
        groups[(r['model'], r['prompt_version'], r['split'], r['task'], r['subgroup'])].append(r)
    rows = []
    for (model, pv, split, task, sub), rs in sorted(groups.items()):
        ok = [r for r in rs if r['score'] is not None]
        k = sum(r['score'] for r in ok)
        lo, hi = wilson(k, len(ok))
        # Nivel ítem: las repeticiones de un mismo ítem NO son observaciones independientes (n efectivo = ítems).
        by_item = collections.defaultdict(list)
        for r in rs:
            by_item[r['item_id']].append(r)
        means, strict = [], []
        for xs in by_item.values():
            got = [x['score'] for x in xs if x['score'] is not None]
            if got:
                means.append(sum(got) / len(got))
            strict.append(sum((x['score'] or 0) for x in xs) / len(xs))  # 'sin extracción' cuenta como fallo
        k_item = sum(means)
        ilo, ihi = wilson(k_item, len(means))
        rows.append({'model': model, 'prompt_version': pv, 'split': split, 'task': task, 'subgroup': sub,
                     'score_name': rs[0]['score_name'], 'records': len(rs), 'scored': len(ok), 'successes': k,
                     'rate': (k / len(ok)) if ok else None, 'ci95_low': lo, 'ci95_high': hi,
                     'items': len(by_item), 'items_scored': len(means),
                     'item_rate': (k_item / len(means)) if means else None, 'item_ci95_low': ilo, 'item_ci95_high': ihi,
                     'item_rate_strict': sum(strict) / len(strict),
                     'format_rate': sum(1 for r in rs if r['method'] in ('final_line', 'verdict_line')) / len(rs),
                     'unscored': len(rs) - len(ok), 'methods': dict(collections.Counter(r['method'] for r in rs)),
                     'latex': sum(1 for r in rs if r['latex']), 'truncated': sum(1 for r in rs if r['truncated']),
                     'think_leak': sum(1 for r in rs if r['think_leak'])})
    # repetibilidad: mismo ítem, misma configuración, varias repeticiones medidas
    byitem = collections.defaultdict(list)
    for r in meas:
        byitem[(r['model'], r['prompt_version'], r['item_id'])].append(r)
    rep = collections.defaultdict(lambda: {'items_multi_rep': 0, 'identical_response': 0, 'score_changes': 0})
    for (model, pv, _), rs in byitem.items():
        if len({r['rep'] for r in rs}) < 2:
            continue
        d = rep[(model, pv)]
        d['items_multi_rep'] += 1
        d['identical_response'] += 1 if len({r['response'] for r in rs}) == 1 else 0
        d['score_changes'] += 1 if len({r['score'] for r in rs}) > 1 else 0
    repeat = [{'model': m, 'prompt_version': pv, **v} for (m, pv), v in sorted(rep.items())]
    return {'rows': rows, 'repeatability': repeat, 'measured_records': len(meas), 'warmup_records': len(scored) - len(meas)}


def pct(x):
    return '   —  ' if x is None else f'{100 * x:5.1f}%'


def print_summary(s):
    print(f"Registros medidos: {s['measured_records']} (calentamiento excluido: {s['warmup_records']})")
    print('Las repeticiones de un ítem NO son independientes: la tasa y el IC se calculan por ÍTEM (n efectivo = ítems).')
    print('IC de Wilson 95 % NAIVE: ignora además la agrupación por problema base. Descriptivo, no inferencia.')
    print("'estricta' cuenta 'sin extracción' como fallo; 'tasa' solo cuenta lo que se pudo leer.\n")
    head = (f"{'modelo':22} {'split':5} {'tarea':8} {'grupo':9} {'reg':>4} {'ítems':>5} {'leídos':>6} "
            f"{'tasa':>7} {'IC95 (ítems)':>17} {'estricta':>8} {'formato':>8}")
    print(head)
    for r in s['rows']:
        ci = f"[{pct(r['item_ci95_low'])},{pct(r['item_ci95_high'])}]" if r['item_ci95_low'] is not None else ''
        print(f"{r['model'][:22]:22} {r['split']:5} {r['task']:8} {r['subgroup']:9} {r['records']:>4} {r['items']:>5} "
              f"{r['items_scored']:>6} {pct(r['item_rate']):>7} {ci:>17} {pct(r['item_rate_strict']):>8} {pct(r['format_rate']):>8}")
    print('\nsolve = exactitud · diagnose = veredicto correcto (con_error: sensibilidad; control: especificidad) · '
          'hint = SIN fuga del resultado')
    for r in s['repeatability']:
        print(f"Repetibilidad {r['model']}: {r['identical_response']}/{r['items_multi_rep']} ítems con respuesta idéntica en todas "
              f"las repeticiones; {r['score_changes']} ítems cambian de puntuación")


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument('--run', action='append', required=True, help='archivo .jsonl de una corrida (repetible)')
    p.add_argument('--dataset', required=True)
    p.add_argument('--output', default=None, help='registros puntuados .jsonl (nuevo; no sobrescribe)')
    p.add_argument('--summary', default=None, help='resumen .json (nuevo; no sobrescribe)')
    p.add_argument('--allow-dataset-mismatch', action='store_true')
    a = p.parse_args(argv)
    scored, warnings = score_runs(a.run, a.dataset, a.allow_dataset_mismatch)
    summ = summarize(scored)
    first = pathlib.Path(a.run[0])
    out = pathlib.Path(a.output) if a.output else first.with_suffix('.scores.jsonl')
    sm = pathlib.Path(a.summary) if a.summary else first.with_suffix('.summary.json')
    for path in (out, sm):
        if path.exists():
            raise SystemExit(f'Ya existe {path}; no se sobrescribe.')
    with out.open('x', encoding='utf-8') as f:
        for r in scored:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')
    with sm.open('x', encoding='utf-8') as f:
        json.dump({'runs': [str(pathlib.Path(r)) for r in a.run], 'dataset': str(a.dataset), 'warnings': warnings, **summ},
                  f, ensure_ascii=False, indent=2)
        f.write('\n')
    for w in warnings:
        print('AVISO:', w)
    print_summary(summ)
    print(f'\nRegistros puntuados: {out}\nResumen: {sm}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
