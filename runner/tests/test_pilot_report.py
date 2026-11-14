"""Pruebas del informe del piloto con datos de juguete calculados a mano."""
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
import pilot_report as pr  # noqa: E402


def rec(item, base, model, rep, score, task='solve', sub='todos', resp='r', warm=False, tokens=100, dur=1e9, wall=1.0):
    return {'item_id': item, 'problem_base_id': base, 'model': f'qwen3:0.6b-{model}', 'rep': rep, 'score': score, 'task': task,
            'subgroup': sub, 'response': resp, 'is_warmup': warm, 'eval_count': tokens, 'eval_duration_ns': dur, 'wall_seconds': wall}


class InformeDeJuguete(unittest.TestCase):
    def test_tabla_estricta_y_legible(self):
        rows = [rec('PB-SUB-02-S', 'PB-SUB-02', 'q4_K_M', 1, 1), rec('PB-SUB-02-S', 'PB-SUB-02', 'q4_K_M', 2, None),
                rec('PB-SUB-03-S', 'PB-SUB-03', 'q4_K_M', 1, None), rec('PB-SUB-03-S', 'PB-SUB-03', 'q4_K_M', 2, None)]
        self.assertEqual(pr.item_table(rows, True), {'PB-SUB-02-S': ('PB-SUB-02', 0.5), 'PB-SUB-03-S': ('PB-SUB-03', 0.0)})
        self.assertEqual(pr.item_table(rows, False), {'PB-SUB-02-S': ('PB-SUB-02', 1.0)})   # el ítem totalmente ilegible se omite

    def test_ic_por_conglomerados_determinista_y_coherente(self):
        tab = {f'PB-MUL-{i:02d}-S': (f'PB-MUL-{i:02d}', 1.0 if i % 2 else 0.0) for i in range(2, 12)}
        a, b = pr.cluster_ci(tab, 2000, 1), pr.cluster_ci(tab, 2000, 1)
        self.assertEqual(a, b)                                                            # misma semilla, mismo resultado
        est, lo, hi = a
        self.assertAlmostEqual(est, 0.5)
        self.assertLessEqual(lo, est)
        self.assertGreaterEqual(hi, est)
        self.assertGreater(hi - lo, 0.2)                                                  # con 10 problemas, el intervalo es ancho
        todo_uno = {f'PB-MUL-{i:02d}-S': (f'PB-MUL-{i:02d}', 1.0) for i in range(2, 8)}
        self.assertEqual(pr.cluster_ci(todo_uno, 500, 1), (1.0, 1.0, 1.0))                # caso degenerado
        self.assertEqual(pr.cluster_ci({}, 10, 1), (None, None, None))

    def test_los_conglomerados_agrupan_por_problema_base(self):
        # 2 ítems del mismo problema base cuentan como un conglomerado: remuestrear el problema los arrastra juntos
        tab = {'PB-DIV-02-S': ('PB-DIV-02', 1.0), 'PB-DIV-02-D': ('PB-DIV-02', 1.0), 'PB-DIV-03-S': ('PB-DIV-03', 0.0), 'PB-DIV-03-D': ('PB-DIV-03', 0.0)}
        est, lo, hi = pr.cluster_ci(tab, 3000, 7)
        self.assertEqual(est, 0.5)
        self.assertEqual((lo, hi), (0.0, 1.0))      # con 2 conglomerados se puede obtener 0 o 1: la incertidumbre es máxima

    def test_diferencia_emparejada(self):
        a = {'PB-SUB-02-S': ('PB-SUB-02', 1.0), 'PB-SUB-03-S': ('PB-SUB-03', 1.0), 'PB-SUB-04-S': ('PB-SUB-04', 0.0), 'PB-SUB-05-S': ('PB-SUB-05', 0.5)}
        b = {'PB-SUB-02-S': ('PB-SUB-02', 0.0), 'PB-SUB-03-S': ('PB-SUB-03', 1.0), 'PB-SUB-04-S': ('PB-SUB-04', 1.0), 'PB-SUB-05-S': ('PB-SUB-05', 0.5)}
        r = pr.paired(a, b, 500, 3)
        self.assertEqual((r['items'], r['a_better'], r['b_better'], r['ties']), (4, 1, 1, 2))
        self.assertAlmostEqual(r['diff'], 0.0)

    def test_build_excluye_calentamiento_y_calcula_costo_y_repetibilidad(self):
        rows = []
        for model, tok in (('q4_K_M', 200), ('q8_0', 100)):
            for base in ('PB-SUB-02', 'PB-SUB-03', 'PB-SUB-04'):
                iid = f'{base}-S'
                rows.append(rec(iid, base, model, 0, 0, warm=True, resp='calentamiento'))
                for rep in (1, 2, 3):
                    rows.append(rec(iid, base, model, rep, 1, resp='igual' if base != 'PB-SUB-04' else f'distinta{rep}', tokens=tok))
        rep = pr.build(rows, 300, 5)
        self.assertEqual((rep['measured_records'], rep['warmup_records']), (18, 6))
        g = {x['model']: x for x in rep['groups']}
        self.assertEqual(g['q4_K_M']['rate_strict'], 1.0)
        self.assertEqual(g['q4_K_M']['problem_bases'], 3)
        r = {x['model']: x for x in rep['repeatability']}
        self.assertEqual((r['q4_K_M']['items_multi_rep'], r['q4_K_M']['identical_response'], r['q4_K_M']['score_changes']), (3, 2, 0))
        t = {x['model']: x for x in rep['timing']}
        self.assertEqual(t['q4_K_M']['median_tokens_per_s'], 200.0)
        self.assertEqual(t['q8_0']['median_tokens_per_s'], 100.0)
        self.assertEqual(len(rep['paired']), 1)                                           # solo existe la pareja q4_K_M vs q8_0
        self.assertIn('Registros medidos: 18', pr.render(rep))


if __name__ == '__main__':
    unittest.main()
