"""Pruebas básicas del runner v0.2. No requieren Ollama ni modelos.

Las pruebas de 'servidor simulado' verifican el CÓDIGO del runner (archivos, manifiesto, errores),
NO el comportamiento de ningún modelo. Ejecutar:  python -I -m unittest discover -s tests -v
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

MODEL = 'qwen3:0.6b-q4_K_M'


class FakeOllama(http.server.BaseHTTPRequestHandler):
    """Imita los endpoints de Ollama que usa el runner. Comportamiento configurable por clase."""
    eval_count = 40
    done_reason = 'stop'
    chat_status = 200
    ps_size, ps_vram = 1000, 1000
    chat_bodies = []

    def log_message(self, *a):
        pass

    def _send(self, obj, status=200):
        raw = json.dumps(obj).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        if self.path == '/api/version':
            self._send({'version': '0.0.0-fake'})
        elif self.path == '/api/tags':
            self._send({'models': [{'name': MODEL, 'model': MODEL, 'digest': 'f' * 64}]})
        elif self.path == '/api/ps':
            self._send({'models': [{'name': MODEL, 'model': MODEL, 'size': self.ps_size,
                                    'size_vram': self.ps_vram, 'context_length': 2048, 'runner': 'fake'}]})
        else:
            self._send({'error': 'not found'}, 404)

    def do_POST(self):
        n = int(self.headers.get('Content-Length', 0))
        body = json.loads(self.rfile.read(n) or b'{}')
        if self.path == '/api/show':
            self._send({'details': {'quantization_level': 'Q4_K_M'}, 'parameters': 'temperature 0.6',
                        'capabilities': ['completion', 'thinking'], 'template': 'T',
                        'model_info': {'qwen3.context_length': 40960}})
        elif self.path == '/api/chat':
            type(self).chat_bodies.append(body)
            if self.chat_status != 200:
                self._send({'error': 'modelo roto (simulado)'}, self.chat_status)
                return
            self._send({'message': {'role': 'assistant', 'content': 'respuesta simulada'},
                        'done_reason': self.done_reason, 'total_duration': 1, 'load_duration': 1,
                        'prompt_eval_count': 10, 'prompt_eval_duration': 1,
                        'eval_count': self.eval_count, 'eval_duration': 1})
        else:
            self._send({'error': 'not found'}, 404)


class UnitTests(unittest.TestCase):
    def test_dataset_valid_and_correct(self):
        rows = rx.load_dataset(ROOT / 'data' / 'pilot_examples.jsonl')
        self.assertEqual(len(rows), 9)
        gold = {'PAN-G3-001': 6 * 4, 'PAN-G3-002': 36 // 6, 'PAN-G3-003': 125 - 38}
        for r in rows:
            self.assertEqual(r['gold_answer'], str(gold[r['id'].rsplit('-', 1)[0]]), r['id'])

    def test_dataset_rejects_duplicates_and_missing_fields(self):
        with tempfile.TemporaryDirectory() as d:
            p = pathlib.Path(d) / 'x.jsonl'
            base = {'id': 'A', 'task': 'solve', 'topic': 't', 'problem': 'p'}
            p.write_text(json.dumps(base) + '\n' + json.dumps(base) + '\n', encoding='utf-8')
            with self.assertRaises(ValueError):
                rx.load_dataset(p)
            bad = dict(base, id='B', task='diagnose')  # falta student_answer
            p.write_text(json.dumps(bad) + '\n', encoding='utf-8')
            with self.assertRaises(ValueError):
                rx.load_dataset(p)

    def test_tildes_en_prompt_y_datos(self):
        self.assertIn('español', rx.SYSTEM)
        self.assertNotIn('profesores', rx.SYSTEM)  # sin metainstrucciones de investigación
        text = (ROOT / 'data' / 'pilot_examples.jsonl').read_text(encoding='utf-8')
        for palabra in ('lápices', 'Cuántos', 'tenía', 'prestó'):
            self.assertIn(palabra, text)
        for mal in ('lapices', 'Cuantos', 'tenia', 'presto'):
            self.assertNotIn(mal, text)

    def test_prompts_por_tarea(self):
        rows = {r['task']: r for r in rx.load_dataset(ROOT / 'data' / 'pilot_examples.jsonl')}
        for task, ex in rows.items():
            self.assertIn(ex['problem'], rx.prompt_for(ex))
        self.assertIn('No reveles el resultado final', rx.prompt_for(rows['hint']))
        with self.assertRaises(ValueError):
            rx.prompt_for({'task': 'otra', 'problem': 'p'})

    def test_open_new_no_sobrescribe(self):
        with tempfile.TemporaryDirectory() as d:
            p = pathlib.Path(d) / 'sub' / 'a.jsonl'
            with rx.open_new(p) as f:
                f.write('uno\n')
            with self.assertRaises(FileExistsError):
                rx.open_new(p)
            self.assertEqual(p.read_text(encoding='utf-8'), 'uno\n')

    def test_host(self):
        self.assertEqual(rx.normalize_host('127.0.0.1:11435'), 'http://127.0.0.1:11435')
        self.assertEqual(rx.normalize_host(None), rx.DEFAULT_HOST)
        self.assertTrue(rx.is_loopback('http://localhost:1'))
        self.assertTrue(rx.is_loopback('http://127.0.0.1:11435'))
        self.assertFalse(rx.is_loopback('http://192.168.1.5:11434'))

    def test_offload_mode(self):
        self.assertEqual(rx.offload_mode(1000, 1000), 'gpu_only')
        self.assertEqual(rx.offload_mode(1000, 0), 'cpu_only')
        self.assertEqual(rx.offload_mode(1000, 400), 'hybrid')
        self.assertEqual(rx.offload_mode(None, 5), 'unknown')
        self.assertEqual(rx.offload_mode(0, 0), 'unknown')

    def test_truncated(self):
        self.assertTrue(rx.is_truncated({'done_reason': 'length'}, 256))
        self.assertTrue(rx.is_truncated({'done_reason': 'stop', 'eval_count': 256}, 256))
        self.assertFalse(rx.is_truncated({'done_reason': 'stop', 'eval_count': 40}, 256))


class FlowTests(unittest.TestCase):
    """Flujo completo del runner contra un Ollama SIMULADO (no prueba ningún modelo)."""

    def setUp(self):
        for k, v in dict(eval_count=40, done_reason='stop', chat_status=200, ps_size=1000, ps_vram=1000).items():
            setattr(FakeOllama, k, v)
        FakeOllama.chat_bodies = []
        self.srv = http.server.ThreadingHTTPServer(('127.0.0.1', 0), FakeOllama)
        self.host = f'http://127.0.0.1:{self.srv.server_address[1]}'
        threading.Thread(target=self.srv.serve_forever, daemon=True).start()
        self.tmp = tempfile.TemporaryDirectory()
        self.out = pathlib.Path(self.tmp.name) / 'run.jsonl'

    def tearDown(self):
        self.srv.shutdown()
        self.srv.server_close()
        self.tmp.cleanup()

    def run_main(self, *extra):
        return rx.main(['--model', MODEL, '--host', self.host, '--output', str(self.out), *extra])

    def read(self):
        recs = [json.loads(x) for x in self.out.read_text(encoding='utf-8').splitlines()]
        man = json.loads(self.out.with_suffix('.manifest.json').read_text(encoding='utf-8'))
        return recs, man

    def test_corrida_completa(self):
        self.assertEqual(self.run_main(), 0)
        recs, man = self.read()
        self.assertEqual(len(recs), 9)
        self.assertEqual(man['status'], 'completed')
        self.assertEqual(man['counts'], {'items': 9, 'errors': 0, 'truncated': 0})
        self.assertEqual(man['ollama']['version'], '0.0.0-fake')
        self.assertEqual(man['ollama']['model_digest'], 'f' * 64)
        self.assertEqual(man['ollama']['show']['details']['quantization_level'], 'Q4_K_M')
        self.assertEqual(man['offload_first']['mode'], 'gpu_only')
        self.assertEqual(man['dataset']['sha256'], rx.sha256_file(ROOT / 'data' / 'pilot_examples.jsonl'))
        self.assertEqual(man['config']['effective_options']['num_predict'], 256)
        for r in recs:
            for k in ('done_reason', 'truncated', 'prompt_eval_duration_ns', 'prompt_sha256', 'run_id'):
                self.assertIn(k, r)
            self.assertFalse(r['truncated'])
        self.assertTrue(all(b.get('think') is False for b in FakeOllama.chat_bodies))  # qwen3 sin razonamiento

    def test_no_sobrescribe_salida(self):
        self.run_main()
        antes = self.out.read_text(encoding='utf-8')
        with self.assertRaises(SystemExit):
            self.run_main()
        self.assertEqual(self.out.read_text(encoding='utf-8'), antes)

    def test_truncamiento_se_marca(self):
        FakeOllama.eval_count, FakeOllama.done_reason = 256, 'length'
        self.run_main('--limit', '2')
        recs, man = self.read()
        self.assertTrue(all(r['truncated'] for r in recs))
        self.assertEqual(man['counts']['truncated'], 2)

    def test_error_conserva_cuerpo_http_y_devuelve_1(self):
        FakeOllama.chat_status = 500
        self.assertEqual(self.run_main('--limit', '2'), 1)
        recs, man = self.read()
        self.assertEqual(man['counts']['errors'], 2)
        self.assertIn('HTTP 500', recs[0]['error'])
        self.assertIn('modelo roto', recs[0]['error'])

    def test_modo_hibrido_se_registra(self):
        FakeOllama.ps_size, FakeOllama.ps_vram = 1000, 400
        self.run_main('--limit', '1')
        _, man = self.read()
        self.assertEqual(man['offload_first']['mode'], 'hybrid')

    def test_host_remoto_rechazado(self):
        with self.assertRaises(SystemExit):
            rx.main(['--model', MODEL, '--host', 'http://192.0.2.1:11434', '--output', str(self.out)])
        self.assertFalse(self.out.exists())


if __name__ == '__main__':
    unittest.main()
