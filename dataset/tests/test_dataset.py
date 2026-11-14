"""Pruebas del dataset v0.1. Ejecutar:  python -I -m unittest discover -s tests -v

Los casos 'a mano' se calcularon a mano, con papel, ANTES de escribir el código; no dependen de él.
"""
import copy
import json
import pathlib
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
import build_dataset as bd  # noqa: E402
import generators as g  # noqa: E402
import validate_dataset as vd  # noqa: E402
from problem_bases import BASES  # noqa: E402


class CasosAMano(unittest.TestCase):
    def test_sustraccion(self):
        self.assertEqual(g.solve('sub', 725, 348), {'value': 377})
        self.assertEqual(g.sub_col_min_from_max(725, 348)[0], {'value': 423})   # |5-8|,|2-4|,|7-3|
        self.assertEqual(g.sub_borrow_no_decrement(725, 348)[0], {'value': 487})  # 15-8, 12-4, 7-3
        self.assertEqual(g.sub_borrow_no_decrement(4310, 1285)[0], {'value': 3135})
        self.assertEqual(g.sub_add_instead(725, 348)[0], {'value': 1073})

    def test_multiplicacion(self):
        self.assertEqual(g.solve('mul', 13, 6), {'value': 78})
        self.assertEqual(g.mul_omit_carry(13, 6)[0], {'value': 68})       # 3x6=18->8 ; 1x6=6
        self.assertEqual(g.mul_omit_carry(25, 4)[0], {'value': 80})       # 5x4=20->0 ; 2x4=8
        self.assertEqual(g.mul_omit_carry(1203, 4)[0], {'value': 4802})
        self.assertEqual(g.mul_forget_shift(48, 12)[0], {'value': 144})   # 96 + 48
        self.assertEqual(g.mul_forget_shift(245, 23)[0], {'value': 1225}) # 735 + 490
        self.assertEqual(g.mul_add_instead(134, 6)[0], {'value': 140})

    def test_division(self):
        self.assertEqual(g.solve('div', 87, 4), {'quotient': 21, 'remainder': 3})
        self.assertEqual(g.div_stop_early(87, 4)[0], {'quotient': 20, 'remainder': 7})
        self.assertEqual(g.div_stop_early(900, 12)[0], {'quotient': 74, 'remainder': 12})
        self.assertEqual(g.div_ignore_remainder(92, 6)[0], {'quotient': 15, 'remainder': 0})
        self.assertEqual(g.div_subtract_instead(50, 5)[0], {'value': 45})
        self.assertEqual(g.solve('div', 900, 12), {'quotient': 75, 'remainder': 0})

    def test_formato(self):
        self.assertEqual(g.fmt({'value': 377}), '377')
        self.assertEqual(g.fmt({'quotient': 21, 'remainder': 3}), 'cociente 21, residuo 3')

    def test_generador_sin_error_real_falla(self):
        with self.assertRaises(ValueError):
            g.make_error('sub_col_min_from_max', 'sub', 500, 200)  # sin préstamos: coincide con la correcta
        with self.assertRaises(ValueError):
            g.make_error('div_ignore_remainder', 'div', 365, 5)     # residuo 0
        with self.assertRaises(ValueError):
            g.make_error('mul_forget_shift', 'mul', 13, 6)          # multiplicador de 1 cifra
        with self.assertRaises(ValueError):
            g.make_error('mul_add_instead', 'sub', 5, 3)            # operación equivocada

    def test_dificultad(self):
        self.assertEqual(g.difficulty('mul', 13, 6), 1)
        self.assertEqual(g.difficulty('mul', 48, 12), 2)
        self.assertEqual(g.difficulty('mul', 312, 45), 3)
        self.assertEqual(g.difficulty('div', 87, 4), 1)
        self.assertEqual(g.difficulty('div', 158, 7), 2)
        self.assertEqual(g.difficulty('div', 845, 26), 3)
        self.assertEqual(g.difficulty('sub', 725, 348), 2)
        self.assertEqual(g.difficulty('sub', 840, 357), 2)    # el cero está en las unidades: solo pide a la columna vecina
        self.assertEqual(g.difficulty('sub', 4310, 1285), 2)  # dos préstamos, sin pasar por un cero
        self.assertEqual(g.difficulty('sub', 2000, 845), 3)   # el préstamo pasa por dos ceros
        self.assertEqual(g.difficulty('sub', 612, 275), 2)
        self.assertEqual(g.difficulty('sub', 650, 320), 1)    # sin préstamos


class DatasetCompleto(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.items = bd.build_items()

    def test_tamano_y_estructura(self):
        self.assertEqual(len(BASES), 30)
        self.assertEqual(len(self.items), 90)
        self.assertEqual(len({b[0] for b in BASES}), 30)
        self.assertEqual(sum(1 for b in BASES if b[6] == 'correct'), 6)
        for comp in ('A3-SUB-24', 'A3-MUL-24', 'A3-DIV-24'):
            self.assertEqual(sum(1 for b in BASES if b[1] == comp), 10)
            self.assertEqual(sum(1 for b in BASES if b[1] == comp and b[6] == 'correct'), 2)
        self.assertEqual(sum(1 for b in BASES if b[7] == 'dev'), 3)

    def test_valido(self):
        self.assertEqual(vd.validate(self.items), [])

    def test_ninguna_respuesta_erronea_es_correcta(self):
        for it in self.items:
            if it['student_answer_is_correct'] is False:
                self.assertNotEqual(it['student_answer'], it['gold_answer'], it['item_id'])

    def test_validador_detecta_manipulaciones(self):
        def mutar(fn):
            copia = copy.deepcopy(self.items)
            fn(copia)
            return vd.validate(copia)

        self.assertTrue(mutar(lambda c: c[0].__setitem__('gold_answer', '999')))
        self.assertTrue(mutar(lambda c: c[1].__setitem__('student_answer', '1')))
        self.assertTrue(mutar(lambda c: c[1].__setitem__('error_generator', 'sub_add_instead')))
        self.assertTrue(mutar(lambda c: c[1].__setitem__('gold_error_observable', 'otro texto')))
        self.assertTrue(mutar(lambda c: c[4].__setitem__('split', 'test')))      # partición distinta en una base
        self.assertTrue(mutar(lambda c: c.append(copy.deepcopy(c[0]))))          # id duplicado
        self.assertTrue(mutar(lambda c: c.pop(2)))                               # base sin hint
        self.assertTrue(mutar(lambda c: c[0].__setitem__('problem_text', 'Sin números.')))
        self.assertTrue(mutar(lambda c: c[0].__setitem__('difficulty', 3)))
        # control con error_generator: debe fallar
        idx = next(i for i, it in enumerate(self.items) if it['student_answer_is_correct'] is True)
        self.assertTrue(mutar(lambda c: c[idx].__setitem__('error_generator', 'sub_add_instead')))

    def test_enunciados_con_ortografia_basica(self):
        todo = ' '.join(it['problem_text'] for it in self.items)
        for mal in ('Cuantos', 'Cuantas', 'libras de cafe', 'tenia ', 'lapices'):
            self.assertNotIn(mal, todo)
        self.assertIn('¿Cuántas', todo)
        self.assertIn('¿Cuántos', todo)


class Construccion(unittest.TestCase):
    def test_no_sobrescribe(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(bd.main(['--output-dir', d]), 0)
            antes = (pathlib.Path(d) / 'items.jsonl').read_text(encoding='utf-8')
            with self.assertRaises(SystemExit):
                bd.main(['--output-dir', d])
            self.assertEqual((pathlib.Path(d) / 'items.jsonl').read_text(encoding='utf-8'), antes)
            lineas = [json.loads(x) for x in antes.splitlines()]
            self.assertEqual(len(lineas), 90)
            self.assertEqual(vd.validate(lineas), [])

    def test_es_deterministico(self):
        self.assertEqual(json.dumps(bd.build_items(), ensure_ascii=False), json.dumps(bd.build_items(), ensure_ascii=False))


if __name__ == '__main__':
    unittest.main()
