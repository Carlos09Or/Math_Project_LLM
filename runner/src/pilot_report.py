"""Informe descriptivo del piloto, según docs/pilot_run_plan.md. Solo biblioteca estándar.

Unidad = ÍTEM (promedio de sus repeticiones). Los ítems de un mismo problema base no son independientes, por lo que los
intervalos se calculan con bootstrap por conglomerados (por problema base). Descriptivo: sin p-values ni afirmaciones causales.

Uso:  python src/pilot_report.py --scores runs_pilot/X.scores.jsonl [--out runs_pilot/X.report.json]
"""
import argparse
import collections
import json
import pathlib
import random
import statistics
import sys

N_BOOT = 10000
SEED = 12345
PAIRS = (('q4_K_M', 'q8_0'), ('q4_K_M', 'fp16'), ('q8_0', 'fp16'))
GROUPS = (('solve', 'todos', 'exactitud'), ('diagnose', 'con_error', 'sensibilidad'),
          ('diagnose', 'control', 'especificidad'), ('hint', 'todos', 'sin fuga'))


def load(path):
    return [json.loads(x) for x in pathlib.Path(path).read_text(encoding='utf-8').splitlines() if x.strip()]


def short(model):
    return model.split(':', 1)[1].replace('0.6b-', '')


def item_table(rows, strict=True):
    """item_id -> (problem_base_id, valor). valor = media de repeticiones.
    strict: «sin extracción» cuenta como 0. Si no es strict, se ignora y el ítem se omite si ninguna repetición se pudo leer."""
    by = collections.defaultdict(list)
    for r in rows:
        by[r['item_id']].append(r)
    out = {}
    for iid, xs in by.items():
        vals = [(x['score'] if x['score'] is not None else 0) for x in xs] if strict \
            else [x['score'] for x in xs if x['score'] is not None]
        if vals:
            out[iid] = (xs[0]['problem_base_id'], sum(vals) / len(vals))
    return out


def cluster_ci(table, n_boot=N_BOOT, seed=SEED):
    """(estimación, límite inferior, límite superior): media por ítem y bootstrap por problema base (percentiles 2,5–97,5)."""
    clusters = collections.defaultdict(list)
    for base, v in table.values():
        clusters[base].append(v)
    keys = sorted(clusters)
    if not keys:
        return None, None, None
    rng = random.Random(seed)

    def stat(sample):
        vals = [v for k in sample for v in clusters[k]]
        return sum(vals) / len(vals)

    est = stat(keys)
    boots = sorted(stat([rng.choice(keys) for _ in keys]) for _ in range(n_boot))
    return est, boots[int(0.025 * n_boot)], boots[int(0.975 * n_boot) - 1]


def paired(tab_a, tab_b, n_boot=N_BOOT, seed=SEED):
    """Diferencia A − B emparejada por ítem, con IC por conglomerados y recuento de ítems a favor de cada lado."""
    common = sorted(set(tab_a) & set(tab_b))
    diff = {i: (tab_a[i][0], tab_a[i][1] - tab_b[i][1]) for i in common}
    est, lo, hi = cluster_ci(diff, n_boot, seed)
    eps = 1e-12
    return {'items': len(common), 'diff': est, 'ci95_low': lo, 'ci95_high': hi,
            'a_better': sum(1 for i in common if diff[i][1] > eps), 'b_better': sum(1 for i in common if diff[i][1] < -eps),
            'ties': sum(1 for i in common if abs(diff[i][1]) <= eps)}


def build(scored, n_boot=N_BOOT, seed=SEED):
    meas = [r for r in scored if not r['is_warmup']]
    models = sorted({r['model'] for r in meas})
    out = {'models': [short(m) for m in models], 'measured_records': len(meas), 'warmup_records': len(scored) - len(meas),
           'n_boot': n_boot, 'seed': seed, 'groups': [], 'paired': [], 'by_operation': [], 'repeatability': [], 'timing': []}
    tables = {}
    for task, sub, label in GROUPS:
        for m in models:
            rows = [r for r in meas if r['model'] == m and r['task'] == task and r['subgroup'] == sub]
            if not rows:
                continue
            strict, readable = item_table(rows, True), item_table(rows, False)
            tables[(task, sub, short(m))] = strict
            est, lo, hi = cluster_ci(strict, n_boot, seed)
            rest, rlo, rhi = cluster_ci(readable, n_boot, seed)
            out['groups'].append({
                'task': task, 'subgroup': sub, 'metric': label, 'model': short(m), 'items': len(strict),
                'problem_bases': len({b for b, _ in strict.values()}), 'records': len(rows),
                'rate_strict': est, 'ci95_low': lo, 'ci95_high': hi,
                'rate_readable': rest, 'readable_ci95_low': rlo, 'readable_ci95_high': rhi, 'items_readable': len(readable),
                'unscored_records': sum(1 for r in rows if r['score'] is None)})
            ops = collections.defaultdict(dict)
            for iid, (b, v) in strict.items():
                ops[iid.split('-')[1]][iid] = (b, v)
            for op, tab in sorted(ops.items()):
                out['by_operation'].append({'task': task, 'subgroup': sub, 'model': short(m), 'operation': op,
                                            'items': len(tab), 'rate_strict': sum(v for _, v in tab.values()) / len(tab)})
        for a, b in PAIRS:
            ta, tb = tables.get((task, sub, a)), tables.get((task, sub, b))
            if ta and tb:
                out['paired'].append({'task': task, 'subgroup': sub, 'metric': label, 'a': a, 'b': b, **paired(ta, tb, n_boot, seed)})
    for m in models:
        rows = [r for r in meas if r['model'] == m]
        byitem = collections.defaultdict(list)
        for r in rows:
            byitem[r['item_id']].append(r)
        multi = {i: xs for i, xs in byitem.items() if len({x['rep'] for x in xs}) >= 2}
        out['repeatability'].append({
            'model': short(m), 'items_multi_rep': len(multi),
            'identical_response': sum(1 for xs in multi.values() if len({x['response'] for x in xs}) == 1),
            'score_changes': sum(1 for xs in multi.values() if len({x['score'] for x in xs}) > 1)})
        tps = [r['eval_count'] / (r['eval_duration_ns'] / 1e9) for r in rows if r.get('eval_count') and r.get('eval_duration_ns')]
        wall = [r['wall_seconds'] for r in rows if r.get('wall_seconds') is not None]
        out['timing'].append({'model': short(m), 'records': len(rows), 'median_tokens_per_s': statistics.median(tps) if tps else None,
                              'median_wall_s': statistics.median(wall) if wall else None,
                              'p90_wall_s': sorted(wall)[int(0.9 * len(wall)) - 1] if wall else None,
                              'source': 'reportado por Ollama (eval_count / eval_duration) y reloj del script; no es medición independiente'})
    return out


def pct(x):
    return '  —  ' if x is None else f'{100 * x:5.1f}%'


def render(rep):
    L = [f"Registros medidos: {rep['measured_records']} (calentamiento excluido: {rep['warmup_records']}) · "
         f"bootstrap por problema base: {rep['n_boot']} remuestreos, semilla {rep['seed']}", '',
         'TASAS POR PRECISIÓN (por ítem; IC95 por problema base). «estricta» cuenta lo no legible como fallo.',
         f"{'tarea':9} {'grupo':10} {'métrica':13} {'modelo':8} {'ítems':>5} {'estricta':>8} {'IC95':>17} {'legible':>8} {'sin leer':>8}"]
    for g in rep['groups']:
        ci = f"[{pct(g['ci95_low'])},{pct(g['ci95_high'])}]"
        L.append(f"{g['task']:9} {g['subgroup']:10} {g['metric']:13} {g['model']:8} {g['items']:>5} {pct(g['rate_strict']):>8} "
                 f"{ci:>17} {pct(g['rate_readable']):>8} {g['unscored_records']:>8}")
    L += ['', 'DIFERENCIAS EMPAREJADAS (A − B, en puntos de la tasa; IC95 por problema base). Descriptivo, no inferencia.',
          f"{'tarea':9} {'grupo':10} {'A':8} {'B':8} {'ítems':>5} {'diferencia':>11} {'IC95':>19} {'A mejor':>8} {'B mejor':>8} {'empates':>8}"]
    for p in rep['paired']:
        d = p['diff']
        ci = f"[{100 * p['ci95_low']:+.1f}, {100 * p['ci95_high']:+.1f}]"
        L.append(f"{p['task']:9} {p['subgroup']:10} {p['a']:8} {p['b']:8} {p['items']:>5} {100 * d:+10.1f} {ci:>19} "
                 f"{p['a_better']:>8} {p['b_better']:>8} {p['ties']:>8}")
    L += ['', 'REPETIBILIDAD (3 repeticiones por ítem)']
    for r in rep['repeatability']:
        L.append(f"  {r['model']:8} {r['identical_response']}/{r['items_multi_rep']} ítems con respuesta idéntica en todas las repeticiones; "
                 f"{r['score_changes']} ítems cambian de puntuación")
    L += ['', 'COSTO (reportado por Ollama, pases medidos)']
    for t in rep['timing']:
        L.append(f"  {t['model']:8} mediana {t['median_tokens_per_s']:.0f} tokens/s · mediana {t['median_wall_s']:.2f} s por respuesta "
                 f"· p90 {t['p90_wall_s']:.2f} s")
    return '\n'.join(L)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument('--scores', required=True, help='archivo .scores.jsonl generado por score.py')
    p.add_argument('--out', default=None, help='informe .json (nuevo; no sobrescribe)')
    p.add_argument('--n-boot', type=int, default=N_BOOT)
    a = p.parse_args(argv)
    try:  # la consola de Windows (cp1252) no admite algunos símbolos del informe
        sys.stdout.reconfigure(encoding='utf-8')
    except (AttributeError, ValueError):
        pass
    rep = build(load(a.scores), a.n_boot)
    out = pathlib.Path(a.out) if a.out else pathlib.Path(a.scores).with_suffix('.report.json')
    if out.exists():
        raise SystemExit(f'Ya existe {out}; no se sobrescribe.')
    with out.open('x', encoding='utf-8') as f:
        json.dump(rep, f, ensure_ascii=False, indent=2)
        f.write('\n')
    txt = render(rep)
    md = out.with_suffix('.txt')
    if md.exists():
        raise SystemExit(f'Ya existe {md}; no se sobrescribe.')
    md.write_text(txt + '\n', encoding='utf-8')
    print(txt)
    print(f'\nInforme: {out}\nTexto: {md}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
