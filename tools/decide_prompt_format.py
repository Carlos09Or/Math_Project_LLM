"""Aplica la regla de decisión de docs/prompt_tuning_dev.md a las matrices de runner/runs_dev/.

La decisión usa SOLO la legibilidad del formato (método 'final_line'); la exactitud se imprime después, informativa.
Uso (desde la raíz del repo):  python tools/decide_prompt_format.py
Escribe runner/runs_dev/format_tuning_decision.json (nuevo; no sobrescribe).
"""
import collections
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'runner' / 'src'))
import score as sc  # noqa: E402

GLOBAL_MIN, DIV_MIN, TIE_PP = 0.90, 0.80, 3.0  # iguales en las rondas 1 y 2; no se cambian


def main(argv=None):
    import argparse
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument('--runs-dir', default=str(ROOT / 'runner' / 'runs_dev'))
    p.add_argument('--probes', default=str(ROOT / 'dataset' / 'data' / 'format_probes.jsonl'))
    p.add_argument('--out', default='format_tuning_decision.json', help='nombre del archivo de decisión (nuevo)')
    a = p.parse_args(argv)
    RUNS, PROBES = pathlib.Path(a.runs_dir), pathlib.Path(a.probes)
    sys.path.insert(0, str(ROOT / 'runner' / 'src'))
    import run_experiment as rx
    ops = {i['item_id']: i['operation'] for i in sc.load_jsonl(PROBES)}
    by_variant = collections.defaultdict(list)
    for mp in sorted(RUNS.glob('*.matrix.json')):
        m = json.loads(mp.read_text(encoding='utf-8'))
        scored, _ = sc.score_runs([str(mp.parent / pathlib.Path(p['output']).name) for p in m['passes']], PROBES)
        by_variant[m['prompt_version']] += [r for r in scored if not r['is_warmup'] and r['task'] == 'solve']
    rows = {}
    for v, rs in sorted(by_variant.items()):
        div = [r for r in rs if ops[r['item_id']] == 'div']
        fmt = lambda xs: (sum(1 for r in xs if r['method'] == 'final_line') / len(xs)) if xs else None
        acc = lambda xs: (sum(r['score'] or 0 for r in xs) / len(xs)) if xs else None
        per_model = {mo: fmt([r for r in rs if r['model'] == mo]) for mo in sorted({r['model'] for r in rs})}
        instr = rx.prompt_for({'task': 'solve', 'problem': '', 'operation': 'div'}, v)
        rows[v] = {'records': len(rs), 'division_records': len(div), 'format_rate': fmt(rs), 'format_rate_division': fmt(div),
                   'format_rate_by_model': per_model, 'unscored': sum(1 for r in rs if r['score'] is None),
                   'instruction_chars': len(instr), 'accuracy_informative': acc(rs)}
    ok = {v: r for v, r in rows.items() if r['format_rate'] >= GLOBAL_MIN and r['format_rate_division'] >= DIV_MIN}
    chosen, reason = None, 'ninguna variante cumple los umbrales (global >= 90 % y divisiones >= 80 %)'
    if ok:
        best = max(r['format_rate'] for r in ok.values())
        tied = [v for v, r in ok.items() if (best - r['format_rate']) * 100 <= TIE_PP]
        chosen = min(tied, key=lambda v: ok[v]['instruction_chars'])
        reason = (f'mayor tasa de formato entre las que cumplen los umbrales; empate (<= {TIE_PP} pp) resuelto por la '
                  f'instrucción más corta entre {sorted(tied)}') if len(tied) > 1 else 'mayor tasa de formato entre las que cumplen los umbrales'
    out = {'rule': {'global_min': GLOBAL_MIN, 'division_min': DIV_MIN, 'tie_pp': TIE_PP}, 'variants': rows,
           'chosen': chosen, 'reason': reason}
    path = RUNS / a.out
    with path.open('x', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
        f.write('\n')
    print(f"{'variante':14} {'reg':>4} {'formato':>8} {'divisiones':>11} {'sin extr.':>9} {'caracteres':>10}   formato por precisión")
    for v, r in rows.items():
        pm = '  '.join(f"{k.split(':')[1][5:]}={100 * x:.0f}%" for k, x in r['format_rate_by_model'].items())
        print(f"{v:14} {r['records']:>4} {100 * r['format_rate']:7.1f}% {100 * r['format_rate_division']:10.1f}% {r['unscored']:>9} {r['instruction_chars']:>10}   {pm}")
    print(f"\nDECISIÓN (solo por formato): {chosen}\nMotivo: {reason}")
    print('\nExactitud (informativa, NO usada para decidir):', {v: round(r['accuracy_informative'], 3) for v, r in rows.items()})
    return 0


if __name__ == '__main__':
    sys.exit(main())
