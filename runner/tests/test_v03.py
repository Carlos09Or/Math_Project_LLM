"""Pruebas v0.3: adaptador al dataset nuevo, calentamiento/repeticiones, corrector y matriz de modelos.

Los casos del corrector son respuestas escritas A MANO con su resultado esperado decidido antes de correr el código.
El Ollama es SIMULADO: estas pruebas verifican el código, no ningún modelo.
"""
import http.server
import json
import pathlib
import sys
import tempfile
import threading
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
import run_experiment as rx  # noqa: E402
import run_matrix as rm  # noqa: E402
import score as sc  # noqa: E402

DS = ROOT.parent / 'dataset' / 'data' / 'items.jsonl'
HAS_DS = DS.exists()
A, B = 'qwen3:0.6b-q4_K_M', 'qwen3:0.6b-q8_0'


class CorrectorAMano(unittest.TestCase):
    def test_solve_con_linea_final(self):
        self.assertEqual(sc.extract_solve('Restamos.\nRespuesta final: 377', 'sub'), ({'value': 377}, 'final_line'))
        self.assertEqual(sc.extract_solve('Respuesta final: 6 × 4 = 24', 'mul'), ({'value': 24}, 'final_line'))
        self.assertEqual(sc.extract_solve('Respuesta final: 4 812', 'mul'), ({'value': 4812}, 'final_line'))
        self.assertEqual(sc.extract_solve('RESPUESTA FINAL: 4.812 panes', 'mul'), ({'value': 4812}, 'final_line'))
        self.assertEqual(sc.extract_solve('Respuesta final: cociente 21, residuo 3', 'div'),
                         ({'quotient': 21, 'remainder': 3}, 'final_line'))

    def test_solve_con_respaldo_y_sin_extraccion(self):
        self.assertEqual(sc.extract_solve('$$ 6 \\times 4 = 24 $$ Por lo tanto, hay **24 canicas**.', 'mul'), ({'value': 24}, 'fallback'))
        self.assertEqual(sc.extract_solve('Quedan 377 naranjas', 'sub'), ({'value': 377}, 'fallback'))
        self.assertEqual(sc.extract_solve('El cociente es 15 y sobran 2.', 'div'), ({'quotient': 15, 'remainder': 2}, 'fallback'))
        self.assertEqual(sc.extract_solve('cociente 73, sin residuo', 'div'), ({'quotient': 73, 'remainder': 0}, 'fallback'))
        self.assertEqual(sc.extract_solve('No lo sé', 'sub'), (None, 'none'))
        self.assertEqual(sc.extract_solve('Respuesta final: 24', 'div')[1], 'none')  # formato de división incompleto: no se adivina

    def test_veredicto(self):
        self.assertEqual(sc.extract_verdict('Veredicto: incorrecta\nSe equivocó.'), ('incorrecta', 'verdict_line'))
        self.assertEqual(sc.extract_verdict('Veredicto: Correcta'), ('correcta', 'verdict_line'))
        self.assertEqual(sc.extract_verdict('La respuesta del estudiante es incorrecta porque...'), ('incorrecta', 'fallback'))
        self.assertEqual(sc.extract_verdict('No es correcta.'), ('incorrecta', 'fallback'))
        self.assertEqual(sc.extract_verdict('La respuesta es correcta.'), ('correcta', 'fallback'))
        self.assertEqual(sc.extract_verdict('Es correcta pero también es incorrecta.'), (None, 'none'))
        self.assertEqual(sc.extract_verdict('Hmm, veamos el problema.'), (None, 'none'))

    def test_puntuacion_por_tarea(self):
        sub = {'operation': 'sub', 'gold_answer_struct': {'value': 377}, 'student_answer_is_correct': None}
        r = {'task': 'solve', 'response': 'Respuesta final: 377', 'truncated': False}
        self.assertEqual(sc.score_record(r, sub)['score'], 1)
        self.assertEqual(sc.score_record(dict(r, response='Respuesta final: 387'), sub)['score'], 0)
        self.assertIsNone(sc.score_record(dict(r, response='no sé'), sub)['score'])
        self.assertIsNone(sc.score_record(dict(r, error='HTTP 500'), sub)['score'])
        err = dict(sub, student_answer_is_correct=False)
        ctl = dict(sub, student_answer_is_correct=True)
        d = {'task': 'diagnose', 'response': 'Veredicto: incorrecta', 'truncated': False}
        self.assertEqual(sc.score_record(d, err)['score'], 1)
        self.assertEqual(sc.score_record(d, ctl)['score'], 0)  # falso positivo en un control
        self.assertEqual(sc.score_record(dict(d, response='Veredicto: correcta'), ctl)['score'], 1)
        h = {'task': 'hint', 'response': 'Revisa cada columna.', 'truncated': False}
        self.assertEqual(sc.score_record(h, err)['score'], 1)
        self.assertEqual(sc.score_record(dict(h, response='El resultado es 377.'), err)['score'], 0)
        self.assertEqual(sc.score_record(dict(h, response='Tenías 725 y quitas 348.'), err)['score'], 1)  # números del enunciado no son fuga
        div = {'operation': 'div', 'gold_answer_struct': {'quotient': 21, 'remainder': 1}, 'student_answer_is_correct': False}
        self.assertEqual(sc.score_record(dict(h, response='Cada uno recibe 21.'), div)['score'], 0)
        self.assertEqual(sc.score_record(dict(h, response='Sobra 1, ¿se puede repartir más?'), div)['score'], 1)  # solo el cociente cuenta

    def test_banderas(self):
        sub = {'operation': 'sub', 'gold_answer_struct': {'value': 377}, 'student_answer_is_correct': None}
        s = sc.score_record({'task': 'solve', 'response': '$$ 725 - 348 = 377 $$', 'truncated': True, 'reasoning': 'x'}, sub)
        self.assertTrue(s['latex'] and s['truncated'] and s['think_leak'])

    def test_wilson(self):
        lo, hi = sc.wilson(5, 10)
        self.assertAlmostEqual(lo, 0.2366, places=3)
        self.assertAlmostEqual(hi, 0.7634, places=3)
        self.assertEqual(sc.wilson(0, 0), (None, None))
        self.assertEqual(sc.wilson(10, 10)[1], 1.0)


class PromptsV03(unittest.TestCase):
    def test_formatos_y_no_filtra_el_estado(self):
        solve_div = {'task': 'solve', 'problem': 'P', 'operation': 'div'}
        solve_sub = {'task': 'solve', 'problem': 'P', 'operation': 'sub'}
        self.assertIn('cociente <número>, residuo <número>', rx.prompt_for(solve_div, 'prompt-v0.3'))
        self.assertIn('Respuesta final: <número>', rx.prompt_for(solve_sub, 'prompt-v0.3'))
        d = rx.prompt_for({'task': 'diagnose', 'problem': 'P', 'student_answer': '5'}, 'prompt-v0.3')
        self.assertIn('Veredicto: correcta', d)
        h = rx.prompt_for({'task': 'hint', 'problem': 'P', 'student_answer': '5'}, 'prompt-v0.3')
        self.assertNotIn('error', h.lower())      # el prompt NO dice que el estudiante se equivocó
        self.assertIn('No reveles el resultado final', h)
        self.assertIn('descubra su error', rx.prompt_for({'task': 'hint', 'problem': 'P', 'student_answer': '5'}, 'prompt-v0.2'))
        with self.assertRaises(ValueError):
            rx.prompt_for(solve_sub, 'prompt-v9')

    def test_variantes_difieren_solo_en_el_formato_de_solve(self):
        d = {'task': 'diagnose', 'problem': 'P', 'student_answer': '5'}
        h = {'task': 'hint', 'problem': 'P', 'student_answer': '5'}
        variantes = [v for v in rx.V03_FAMILY if v != 'prompt-v0.3']
        for v in variantes:
            self.assertEqual(rx.prompt_for(d, v), rx.prompt_for(d, 'prompt-v0.3'))   # diagnose y hint no se tocan
            self.assertEqual(rx.prompt_for(h, v), rx.prompt_for(h, 'prompt-v0.3'))
        for op in ('sub', 'div'):
            s = {'task': 'solve', 'problem': 'ENUNCIADO-X', 'operation': op}
            textos = {v: rx.prompt_for(s, v) for v in rx.V03_FAMILY}
            self.assertEqual(len(set(textos.values())), len(rx.V03_FAMILY))          # todas son distintas
            for v, t in textos.items():
                self.assertIn('Respuesta final', t)
                self.assertIn('Resuelve el siguiente problema y explica brevemente el procedimiento.', t)
                self.assertEqual(t.count('ENUNCIADO-X'), 1)                          # el enunciado real aparece una vez
            self.assertTrue(textos['prompt-v0.5a'].startswith('Ejemplo'))
            self.assertLess(textos['prompt-v0.5a'].index('Ejemplo'), textos['prompt-v0.5a'].index('ENUNCIADO-X'))
            self.assertLess(textos['prompt-v0.5b'].index('Respuesta final'), textos['prompt-v0.5b'].index('ENUNCIADO-X'))  # formato antes
            self.assertTrue(textos['prompt-v0.5c'].endswith('No copies esta indicación.'))
        self.assertIn('< >', rx.prompt_for({'task': 'solve', 'problem': 'P', 'operation': 'div'}, 'prompt-v0.4a'))
        self.assertNotIn('<número>', rx.prompt_for({'task': 'solve', 'problem': 'P', 'operation': 'div'}, 'prompt-v0.4a'))


class PromptCongelado(unittest.TestCase):
    """Si esta prueba falla, alguien cambió el prompt congelado: es una versión NUEVA y hay que reportarlo."""

    def test_huella_de_las_plantillas(self):
        import hashlib
        cases = [{'task': 'solve', 'problem': 'PROBLEMA', 'operation': 'sub'}, {'task': 'solve', 'problem': 'PROBLEMA', 'operation': 'mul'},
                 {'task': 'solve', 'problem': 'PROBLEMA', 'operation': 'div'},
                 {'task': 'diagnose', 'problem': 'PROBLEMA', 'student_answer': 'RESP'},
                 {'task': 'hint', 'problem': 'PROBLEMA', 'student_answer': 'RESP'}]
        texts = [rx.prompt_for(c, rx.FROZEN_PROMPT_VERSION) for c in cases]
        h = hashlib.sha256(('\n=====\n'.join(texts) + '\n=====\n' + rx.SYSTEM).encode('utf-8')).hexdigest()
        self.assertEqual(rx.FROZEN_PROMPT_VERSION, 'prompt-v0.5b')
        self.assertEqual(h, rx.FROZEN_PROMPT_SHA256)

    def test_el_orquestador_usa_el_congelado_por_defecto(self):
        a = rm.parse_args(['--models', 'x'])
        self.assertEqual(a.prompt_version, rx.FROZEN_PROMPT_VERSION)
        self.assertEqual(a.split, 'dev')  # la evaluación en pilot hay que pedirla explícitamente


class Fake(http.server.BaseHTTPRequestHandler):
    """Ollama simulado que responde según el prompt (no es ningún modelo)."""
    models = [A, B]
    loaded = []
    unloaded = []
    chats = []

    def log_message(self, *a):
        pass

    def _send(self, obj, status=200):
        raw = json.dumps(obj).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        t = type(self)
        if self.path == '/api/version':
            self._send({'version': '0.0.0-fake'})
        elif self.path == '/api/tags':
            self._send({'models': [{'name': m, 'model': m, 'digest': 'f' * 64} for m in t.models]})
        elif self.path == '/api/ps':
            self._send({'models': [{'name': m, 'model': m, 'size': 1000, 'size_vram': 1000, 'context_length': 2048} for m in t.loaded]})
        else:
            self._send({'error': 'nf'}, 404)

    def do_POST(self):
        t = type(self)
        body = json.loads(self.rfile.read(int(self.headers.get('Content-Length', 0))) or b'{}')
        if self.path == '/api/show':
            self._send({'details': {}, 'parameters': '', 'capabilities': [], 'template': 'T', 'model_info': {}})
        elif self.path == '/api/generate':
            if body.get('keep_alive') == 0 and body['model'] in t.loaded:
                t.loaded.remove(body['model'])
                t.unloaded.append(body['model'])
            self._send({'done': True})
        elif self.path == '/api/chat':
            user = body['messages'][-1]['content']
            if body['model'] not in t.loaded:
                t.loaded.append(body['model'])
            t.chats.append(body['model'])
            if 'Veredicto' in user:
                text = 'Veredicto: incorrecta\nSe equivocó.'
            elif 'Respuesta final' in user:
                text = 'Pienso un poco.\nRespuesta final: 1'
            else:
                text = 'Revisa cada paso con cuidado.'
            self._send({'message': {'role': 'assistant', 'content': text}, 'done_reason': 'stop', 'total_duration': 1,
                        'load_duration': 1, 'prompt_eval_count': 5, 'prompt_eval_duration': 1, 'eval_count': 20, 'eval_duration': 1})
        else:
            self._send({'error': 'nf'}, 404)


@unittest.skipUnless(HAS_DS, 'requiere ../dataset/data/items.jsonl (estructura del repositorio)')
class FlujoConDatasetNuevo(unittest.TestCase):
    def setUp(self):
        Fake.models, Fake.loaded, Fake.unloaded, Fake.chats = [A, B], [], [], []
        self.srv = http.server.ThreadingHTTPServer(('127.0.0.1', 0), Fake)
        self.host = f'http://127.0.0.1:{self.srv.server_address[1]}'
        threading.Thread(target=self.srv.serve_forever, daemon=True).start()
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = pathlib.Path(self.tmp.name)
        self._gpu = rm.gpu_used_mib
        self._wait = (rm.GPU_WAIT_TIMEOUT, rm.GPU_WAIT_POLL)
        rm.GPU_WAIT_TIMEOUT, rm.GPU_WAIT_POLL = 0.05, 0.01  # sin esperas largas en las pruebas
        rm.gpu_used_mib = lambda: 300  # independiente de la GPU real

    def tearDown(self):
        rm.gpu_used_mib = self._gpu
        rm.GPU_WAIT_TIMEOUT, rm.GPU_WAIT_POLL = self._wait
        self.srv.shutdown()
        self.srv.server_close()
        self.tmp.cleanup()

    def run_exp(self, out, *extra, model=A):
        return rx.main(['--model', model, '--host', self.host, '--data', str(DS), '--output', str(self.dir / out), *extra])

    def read(self, out):
        recs = [json.loads(x) for x in (self.dir / out).read_text(encoding='utf-8').splitlines()]
        man = json.loads((self.dir / out).with_suffix('.manifest.json').read_text(encoding='utf-8'))
        return recs, man

    def test_carga_dataset_nuevo(self):
        rows = rx.load_dataset(DS)
        self.assertEqual(len(rows), 90)
        self.assertEqual(rows[0]['id'], rows[0]['item_id'])
        self.assertEqual(rows[0]['problem'], rows[0]['problem_text'])

    def test_particiones(self):
        self.run_exp('dev.jsonl', '--split', 'dev')
        self.run_exp('pilot.jsonl', '--split', 'pilot')
        self.assertEqual(len(self.read('dev.jsonl')[0]), 9)
        self.assertEqual(len(self.read('pilot.jsonl')[0]), 81)
        with self.assertRaises(SystemExit):
            rx.main(['--model', A, '--host', self.host, '--split', 'dev', '--output', str(self.dir / 'x.jsonl')])  # dataset antiguo: sin split

    def test_filtro_de_tareas(self):
        self.run_exp('t.jsonl', '--split', 'dev', '--tasks', 'solve')
        recs, _ = self.read('t.jsonl')
        self.assertEqual({r['task'] for r in recs}, {'solve'})
        self.assertEqual(len(recs), 3)
        with self.assertRaises(SystemExit):
            self.run_exp('u.jsonl', '--tasks', 'otra')

    def test_calentamiento_y_repeticiones(self):
        self.assertEqual(self.run_exp('w.jsonl', '--split', 'dev', '--warmup', '1', '--repeats', '2',
                                      '--prompt-version', 'prompt-v0.3'), 0)
        recs, man = self.read('w.jsonl')
        self.assertEqual(len(recs), 27)
        self.assertEqual(sum(1 for r in recs if r['is_warmup']), 9)
        self.assertEqual({r['rep'] for r in recs if r['is_warmup']}, {0})
        self.assertEqual({r['rep'] for r in recs if not r['is_warmup']}, {1, 2})
        self.assertEqual(man['passes'], {'warmup': 1, 'repeats': 2, 'rep_start': 1})
        self.assertEqual(man['counts']['items'], 27)
        self.assertEqual(man['measured']['items'], 18)
        self.assertEqual(man['prompt']['version'], 'prompt-v0.3')
        self.assertTrue(all(r['prompt_version'] == 'prompt-v0.3' for r in recs))
        self.assertIn('problem_base_id', recs[0])

    def test_corrector_de_extremo_a_extremo(self):
        self.run_exp('s.jsonl', '--split', 'dev', '--repeats', '2', '--prompt-version', 'prompt-v0.3')
        scored, warns = sc.score_runs([self.dir / 's.jsonl'], DS)
        self.assertEqual((len(scored), warns), (18, []))
        s = sc.summarize(scored)
        rows = {(r['task'], r['subgroup']): r for r in s['rows']}
        self.assertEqual((rows['solve', 'todos']['records'], rows['solve', 'todos']['scored'], rows['solve', 'todos']['successes']), (6, 4, 0))
        self.assertEqual(rows['solve', 'todos']['unscored'], 2)          # la división sin formato no se adivina
        sv = rows['solve', 'todos']
        self.assertEqual((sv['items'], sv['items_scored'], sv['item_rate'], sv['item_rate_strict']), (3, 2, 0.0, 0.0))
        dg = rows['diagnose', 'con_error']
        self.assertEqual((dg['records'], dg['items']), (6, 3))           # 2 repeticiones no duplican el n efectivo
        self.assertEqual(dg['item_rate'], 1.0)
        self.assertEqual((rows['diagnose', 'con_error']['scored'], rows['diagnose', 'con_error']['successes']), (6, 6))
        self.assertEqual((rows['hint', 'todos']['scored'], rows['hint', 'todos']['successes']), (6, 6))
        self.assertEqual(s['repeatability'][0]['identical_response'], s['repeatability'][0]['items_multi_rep'])
        # el calentamiento no cuenta
        self.run_exp('s2.jsonl', '--split', 'dev', '--warmup', '1', '--repeats', '1', '--prompt-version', 'prompt-v0.3')
        scored2, _ = sc.score_runs([self.dir / 's2.jsonl'], DS)
        self.assertEqual(sc.summarize(scored2)['measured_records'], 9)
        self.assertEqual(sc.summarize(scored2)['warmup_records'], 9)

    def test_corrector_rechaza_dataset_distinto(self):
        self.run_exp('m.jsonl', '--split', 'dev')
        other = self.dir / 'otro.jsonl'
        other.write_text(DS.read_text(encoding='utf-8') + '\n', encoding='utf-8')
        with self.assertRaises(SystemExit):
            sc.score_runs([self.dir / 'm.jsonl'], other)

    def test_plan_de_pasadas(self):
        p = rm.plan_passes(['a', 'b', 'c'], 3, 1, True)
        self.assertEqual([x['model'] for x in p], ['a', 'b', 'c', 'b', 'c', 'a', 'c', 'a', 'b'])
        self.assertEqual([x['warmup'] for x in p], [1, 1, 1, 0, 0, 0, 0, 0, 0])
        self.assertEqual([x['rep_start'] for x in p], [1, 1, 1, 2, 2, 2, 3, 3, 3])
        b = rm.plan_passes(['a', 'b'], 3, 1, False)
        self.assertEqual(b, [{'model': 'a', 'warmup': 1, 'repeats': 3, 'rep_start': 1}, {'model': 'b', 'warmup': 1, 'repeats': 3, 'rep_start': 1}])

    def matrix(self, *extra):
        return rm.main(['--models', f'{A},{B}', '--host', self.host, '--data', str(DS), '--split', 'dev', '--runs-dir', str(self.dir),
                        '--warmup', '1', '--repeats', '2', *extra])

    def test_matriz_intercalada(self):
        self.assertEqual(self.matrix('--interleave'), 0)
        m = json.loads(next(self.dir.glob('*.matrix.json')).read_text(encoding='utf-8'))
        self.assertEqual([p['model'] for p in m['passes']], [A, B, B, A])
        self.assertEqual([p['rep_start'] for p in m['passes']], [1, 1, 2, 2])
        self.assertTrue(m['sequential'] and m['interleave'] and m['status'] == 'completed')
        self.assertEqual(len(list(self.dir.glob('*.jsonl'))), 4)
        first = json.loads(next(self.dir.glob('*_rep1.jsonl')).with_suffix('.manifest.json').read_text(encoding='utf-8'))
        self.assertEqual(first['matrix_id'], m['matrix_id'])

    def test_matriz_por_bloques_descarga_entre_modelos(self):
        self.assertEqual(self.matrix(), 0)
        m = json.loads(next(self.dir.glob('*.matrix.json')).read_text(encoding='utf-8'))
        self.assertEqual([p['model'] for p in m['passes']], [A, B])
        self.assertIn(A, Fake.unloaded)
        self.assertEqual(Fake.chats[:27], [A] * 27)       # el bloque de A completo antes de B: nunca en paralelo
        self.assertEqual(Fake.chats[27:], [B] * 27)

    def test_espera_a_que_la_gpu_se_libere_tras_descargar(self):
        """Regresión: tras --unload-first la memoria baja con retraso; no debe abortar por una lectura transitoria."""
        rm.GPU_WAIT_TIMEOUT = 5.0
        lecturas = iter([2800, 2800, 1800, 300] + [300] * 50)
        rm.gpu_used_mib = lambda: next(lecturas)
        Fake.loaded[:] = [A]
        self.assertEqual(self.matrix('--unload-first'), 0)

    def test_matriz_protecciones(self):
        Fake.loaded[:] = [A]
        with self.assertRaises(SystemExit):
            self.matrix()                                  # servidor con modelos cargados
        self.assertEqual(self.matrix('--unload-first'), 0)
        rm.gpu_used_mib = lambda: 4000
        with self.assertRaises(SystemExit):
            self.matrix()                                  # GPU ocupada
        rm.gpu_used_mib = lambda: 300
        Fake.models[:] = [A]
        with self.assertRaises(SystemExit):
            self.matrix()                                  # modelo no instalado
        with self.assertRaises(SystemExit):
            rm.main(['--models', 'a,b,c,d', '--interleave', '--host', self.host, '--runs-dir', str(self.dir)])  # > 3 modelos
        with self.assertRaises(SystemExit):
            rm.main(['--models', A, '--host', 'http://192.0.2.1:11434', '--runs-dir', str(self.dir)])  # host remoto


if __name__ == '__main__':
    unittest.main()
