"""Construye data/items.jsonl (90 ítems) y data/problem_bases.csv a partir de problem_bases.py.

Uso:  python src/build_dataset.py            (falla si los archivos ya existen; nunca sobrescribe)
      python src/build_dataset.py --output-dir otra_carpeta
Los ítems son sintéticos y NO tienen revisión docente (reviewer_status = 'unreviewed').
"""
import argparse
import csv
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import generators as g  # noqa: E402
from problem_bases import BASES  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1]

CURRICULUM = {  # competencia -> (tema, página impresa y PDF en M-2024; ver docs/curriculum_map.csv)
    'A3-SUB-24': ('sustraccion', '186-189 (PDF 188-191)'),
    'A3-MUL-24': ('multiplicacion', '188-193 (PDF 190-195)'),
    'A3-DIV-24': ('division', '192-197 (PDF 194-199)'),
}
CURRICULUM_DOC = 'M-2024'
CURRICULUM_VERSION = 'Programa de tercer grado, Educación Básica General, 2024'
RUBRIC_VERSION = 'rubric_v0.1_not_written'  # la rúbrica aún no existe; ver docs/dataset_design.md §7
TASKS = (('S', 'solve'), ('D', 'diagnose'), ('H', 'hint'))

FIELDS = ['item_id', 'problem_base_id', 'grade', 'locale', 'topic', 'competency_id', 'curriculum_doc',
          'curriculum_version', 'curriculum_page', 'task', 'problem_text', 'student_answer', 'gold_answer',
          'gold_error', 'gold_error_observable', 'gold_error_type', 'student_answer_is_correct',
          'error_generator', 'difficulty', 'provenance', 'reviewer_status', 'rubric_version', 'split',
          'operation', 'operands', 'gold_answer_struct', 'student_answer_struct']


def build_items():
    items = []
    for base_id, comp, op, a, b, text, kind, split in BASES:
        topic, page = CURRICULUM[comp]
        truth = g.solve(op, a, b)
        if kind == 'correct':
            student, gen, obs, label, correct = truth, None, None, None, True
        else:
            gen = kind.split(':', 1)[1]
            student, obs, label = g.make_error(gen, op, a, b)
            correct = False
        for suffix, task in TASKS:
            has_student = task != 'solve'
            items.append({
                'item_id': f'{base_id}-{suffix}', 'problem_base_id': base_id, 'grade': 3, 'locale': 'es-PA',
                'topic': topic, 'competency_id': comp, 'curriculum_doc': CURRICULUM_DOC,
                'curriculum_version': CURRICULUM_VERSION, 'curriculum_page': page, 'task': task,
                'problem_text': text,
                'student_answer': g.fmt(student) if has_student else None,
                'gold_answer': g.fmt(truth),
                'gold_error': obs if has_student else None,
                'gold_error_observable': obs if has_student else None,
                'gold_error_type': label if has_student else None,
                'student_answer_is_correct': correct if has_student else None,
                'error_generator': gen if has_student else None,
                'difficulty': g.difficulty(op, a, b), 'provenance': 'synthetic_original',
                'reviewer_status': 'unreviewed', 'rubric_version': RUBRIC_VERSION, 'split': split,
                'operation': op, 'operands': {'a': a, 'b': b}, 'gold_answer_struct': truth,
                'student_answer_struct': student if has_student else None,
            })
    return items


def write_new(path, writer_fn, newline=None):
    path = pathlib.Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8', newline=newline) as f:  # 'x': nunca sobrescribe
        writer_fn(f)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument('--output-dir', default=str(ROOT / 'data'))
    args = p.parse_args(argv)
    out = pathlib.Path(args.output_dir)
    items = build_items()
    items_path, bases_path = out / 'items.jsonl', out / 'problem_bases.csv'
    for path in (items_path, bases_path):
        if path.exists():
            raise SystemExit(f'Ya existe {path}; no se sobrescribe. Bórralo tú o usa --output-dir.')

    def w_items(f):
        for it in items:
            f.write(json.dumps({k: it[k] for k in FIELDS}, ensure_ascii=False, separators=(',', ':')) + '\n')

    def w_bases(f):
        w = csv.writer(f)
        w.writerow(['problem_base_id', 'competency_id', 'operation', 'a', 'b', 'difficulty', 'student_kind',
                    'error_generator', 'split'])
        for base_id, comp, op, a, b, _t, kind, split in BASES:
            w.writerow([base_id, comp, op, a, b, g.difficulty(op, a, b),
                        'correct' if kind == 'correct' else 'error',
                        '' if kind == 'correct' else kind.split(':', 1)[1], split])

    write_new(items_path, w_items)
    write_new(bases_path, w_bases, newline='')
    print(f'{len(items)} ítems de {len(BASES)} problemas base -> {items_path}')
    print(f'resumen de problemas base -> {bases_path}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
