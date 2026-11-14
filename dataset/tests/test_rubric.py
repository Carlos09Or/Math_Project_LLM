"""Integridad de la rúbrica: estructura, autenticidad de los anclas reales y ausencia de contaminación con `pilot`."""
import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
RUBRIC = ROOT / 'dataset' / 'rubric' / 'rubric_v0.1.json'
ITEMS = ROOT / 'dataset' / 'data' / 'items.jsonl'
DEV_RESULTS = ROOT / 'results' / 'scorer_validation_dev'
DOC = ROOT / 'docs' / 'rubric_v0.1.md'


def jl(path):
    return [json.loads(x) for x in pathlib.Path(path).read_text(encoding='utf-8').splitlines() if x.strip()]


@unittest.skipUnless(RUBRIC.exists(), 'falta la rúbrica')
class RubricaIntegridad(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r = json.loads(RUBRIC.read_text(encoding='utf-8'))
        cls.items = {i['item_id']: i for i in jl(ITEMS)}
        cls.crit = {c['id']: c for c in cls.r['criteria']}

    def test_estructura(self):
        self.assertEqual(self.r['version'], 'rubric_v0.1')
        self.assertEqual(len(self.crit), len(self.r['criteria']))                       # ids únicos
        for c in self.r['criteria']:
            self.assertIn(c['task'], ('solve', 'diagnose', 'hint', 'todas'))
            self.assertIn(c['applies_to'], ('todos', 'con_error', 'control'))
            self.assertEqual(sorted(c['levels']), ['0', '1', '2'], c['id'])
            self.assertTrue(all(len(v) > 20 for v in c['levels'].values()), c['id'])    # descriptores no vacíos
        ids = [a['id'] for a in self.r['anchors']]
        self.assertEqual(len(ids), len(set(ids)))

    def test_un_ancla_por_nivel_en_cada_criterio(self):
        for cid in self.crit:
            self.assertEqual(sorted(a['level'] for a in self.r['anchors'] if a['criterion'] == cid), [0, 1, 2], cid)
        for a in self.r['anchors']:
            self.assertIn(a['criterion'], self.crit)
            self.assertIn(a['level'], (0, 1, 2))
            self.assertTrue(a['response'].strip() and a['rationale'].strip())

    def test_anclas_reales_son_autenticas_y_de_dev(self):
        if not DEV_RESULTS.exists():
            self.skipTest('falta results/scorer_validation_dev')
        scored = jl(next(DEV_RESULTS.glob('*.scores.jsonl')))
        reales = [a for a in self.r['anchors'] if a['provenance'] == 'real']
        self.assertGreaterEqual(len(reales), 15)
        for a in reales:
            s = a['source']
            self.assertEqual(s['split'], 'dev')
            self.assertEqual(self.items[s['item_id']]['split'], 'dev', a['id'])          # nunca de pilot
            match = [x for x in scored if x['item_id'] == s['item_id'] and x['model'] == s['model'] and x['rep'] == 1 and not x['is_warmup']]
            self.assertEqual(len(match), 1, a['id'])
            self.assertEqual(a['response'], match[0]['response'], f'{a["id"]}: la respuesta citada no es textual')
            self.assertEqual(a['problem'], self.items[s['item_id']]['problem_text'])

    def test_sin_contaminacion_con_pilot(self):
        pilot_texts = {i['problem_text'] for i in self.items.values() if i['split'] == 'pilot'}
        dev_texts = {i['problem_text'] for i in self.items.values() if i['split'] == 'dev'}
        for a in self.r['anchors']:
            self.assertNotIn(a['problem'], pilot_texts, a['id'])
            self.assertIn(a['problem'], dev_texts, a['id'])                               # solo problemas de dev

    def test_anclas_sinteticas_declaradas(self):
        sint = [a for a in self.r['anchors'] if a['provenance'] == 'sintetico']
        self.assertTrue(sint)
        for a in sint:
            self.assertIsNone(a['source'])
        # los controles (D2) no tienen respuestas reales en dev: deben ser sintéticos
        self.assertTrue(all(a['provenance'] == 'sintetico' for a in self.r['anchors'] if a['criterion'] == 'D2'))

    @unittest.skipUnless(DOC.exists(), 'falta docs/rubric_v0.1.md')
    def test_documento_consistente_con_el_json(self):
        md = DOC.read_text(encoding='utf-8')
        for cid, c in self.crit.items():
            self.assertIn(f'**{cid}**', md)
            for lv in '012':
                self.assertIn(c['levels'][lv], md, f'{cid} nivel {lv}')
        for a in self.r['anchors']:
            self.assertIn(a['id'], md)
            self.assertIn(a['response'].replace('\n', ' / ')[:60], md.replace('\n', ' / '), a['id'])


if __name__ == '__main__':
    unittest.main()
