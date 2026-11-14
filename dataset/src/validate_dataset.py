"""Validador del dataset: recalcula todo desde las operaciones y las reglas, sin confiar en el archivo.

Uso:  python src/validate_dataset.py data/items.jsonl
Código de salida 0 si no hay errores, 1 si los hay.
"""
import collections
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import generators as g  # noqa: E402
from build_dataset import (CURRICULUM, CURRICULUM_DOC, FIELDS, TASKS)  # noqa: E402

SPLITS = {'dev', 'pilot', 'train', 'val', 'test'}
STATUSES = {'unreviewed', 'reviewed_1', 'reviewed_2', 'disputed'}
TASK_NAMES = {t for _, t in TASKS}
SUFFIX = {t: s for s, t in TASKS}


def _numbers(text):
    return set(re.findall(r'\d+', text))


def validate(items):
    """Devuelve la lista de errores (vacía si el dataset es válido)."""
    errs = []
    seen_ids, by_base, texts = set(), collections.defaultdict(list), collections.defaultdict(set)
    for n, it in enumerate(items, 1):
        iid = it.get('item_id', f'#{n}')

        def err(msg):
            errs.append(f'{iid}: {msg}')

        if list(it.keys()) != FIELDS:
            err('campos distintos a los del esquema (o en otro orden)')
            continue
        if iid in seen_ids:
            err('item_id duplicado')
        seen_ids.add(iid)
        base = it['problem_base_id']
        by_base[base].append(it)
        texts[it['problem_text']].add(base)
        if it['task'] not in TASK_NAMES:
            err(f'tarea desconocida {it["task"]}')
            continue
        if iid != f'{base}-{SUFFIX[it["task"]]}':
            err('item_id no coincide con problem_base_id + tarea')
        if it['grade'] != 3 or it['locale'] != 'es-PA':
            err('grado o locale inesperados')
        if it['split'] not in SPLITS or it['reviewer_status'] not in STATUSES:
            err('split o reviewer_status fuera de catálogo')
        if it['competency_id'] not in CURRICULUM or it['curriculum_doc'] != CURRICULUM_DOC:
            err('competencia o documento curricular desconocidos')
        else:
            topic, page = CURRICULUM[it['competency_id']]
            if it['topic'] != topic or it['curriculum_page'] != page:
                err('tema o página curricular no coinciden con el mapa')

        op, ops = it['operation'], it['operands']
        a, b = ops['a'], ops['b']
        try:
            truth = g.solve(op, a, b)
        except ValueError as e:
            err(f'operación inválida: {e}')
            continue
        if it['gold_answer_struct'] != truth or it['gold_answer'] != g.fmt(truth):
            err('gold_answer no coincide con el recálculo')
        if it['difficulty'] != g.difficulty(op, a, b):
            err('difficulty no coincide con la regla')
        nums = _numbers(it['problem_text'])
        if not {str(a), str(b)} <= nums:
            err('el enunciado no contiene los operandos')
        leaked = {str(v) for v in truth.values() if v != 0} & nums
        if leaked:
            err(f'el enunciado contiene el resultado ({sorted(leaked)})')

        if it['task'] == 'solve':
            for k in ('student_answer', 'gold_error', 'gold_error_observable', 'gold_error_type',
                      'student_answer_is_correct', 'error_generator', 'student_answer_struct'):
                if it[k] is not None:
                    err(f'{k} debe ser null en solve')
            continue

        correct = it['student_answer_is_correct']
        if correct is True:
            if it['student_answer_struct'] != truth or it['student_answer'] != g.fmt(truth):
                err('control: la respuesta del estudiante debe ser la correcta')
            for k in ('gold_error', 'gold_error_observable', 'gold_error_type', 'error_generator'):
                if it[k] is not None:
                    err(f'{k} debe ser null en un control')
        elif correct is False:
            gen = it['error_generator']
            if gen not in g.ERRORS:
                err(f'generador desconocido {gen}')
                continue
            try:
                wrong, obs, label = g.make_error(gen, op, a, b)
            except ValueError as e:
                err(f'el generador no reproduce un error: {e}')
                continue
            if it['student_answer_struct'] != wrong or it['student_answer'] != g.fmt(wrong):
                err('student_answer no se reproduce con su generador')
            if it['gold_error_observable'] != obs or it['gold_error'] != obs:
                err('gold_error_observable no coincide con la regeneración')
            if it['gold_error_type'] != label:
                err('gold_error_type no coincide con el generador')
            if it['student_answer'] == it['gold_answer']:
                err('la respuesta errónea coincide con la correcta')
        else:
            err('student_answer_is_correct debe ser true o false en diagnose/hint')

    for base, group in by_base.items():
        tasks = sorted(i['task'] for i in group)
        if tasks != sorted(TASK_NAMES):
            errs.append(f'{base}: debe tener exactamente las tareas solve, diagnose y hint (tiene {tasks})')
        if len({i['split'] for i in group}) != 1:
            errs.append(f'{base}: sus ítems están en particiones distintas')
        if len({(i['operation'], i['operands']['a'], i['operands']['b']) for i in group}) != 1:
            errs.append(f'{base}: sus ítems tienen operaciones distintas')
    for text, bases in texts.items():
        if len(bases) > 1:
            errs.append(f'enunciado repetido en {sorted(bases)}')
    return errs


def summary(items):
    bases = {i['problem_base_id']: i for i in items}
    ctrl = sum(1 for i in items if i['task'] == 'diagnose' and i['student_answer_is_correct'])
    return {
        'items': len(items), 'problemas_base': len(bases),
        'por_tarea': dict(collections.Counter(i['task'] for i in items)),
        'por_competencia': dict(collections.Counter(b['competency_id'] for b in bases.values())),
        'por_dificultad_(problemas)': dict(sorted(collections.Counter(b['difficulty'] for b in bases.values()).items())),
        'por_particion_(problemas)': dict(collections.Counter(b['split'] for b in bases.values())),
        'controles_con_respuesta_correcta_(problemas)': ctrl,
        'generadores': dict(collections.Counter(b['error_generator'] for b in bases.values() if b['error_generator'])),
        'revision': dict(collections.Counter(i['reviewer_status'] for i in items)),
    }


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 1:
        raise SystemExit('Uso: python src/validate_dataset.py data/items.jsonl')
    items = [json.loads(x) for x in pathlib.Path(argv[0]).read_text(encoding='utf-8').splitlines() if x.strip()]
    errs = validate(items)
    if errs:
        print(f'{len(errs)} ERRORES:')
        for e in errs:
            print(' -', e)
        return 1
    print('VÁLIDO.', json.dumps(summary(items), ensure_ascii=False))
    return 0


if __name__ == '__main__':
    sys.exit(main())
