"""Copia los resultados crudos a results/ para publicarlos, redactando las rutas locales.

- Los .jsonl (registros y respuestas puntuadas) y los .txt se copian IDÉNTICOS (sus SHA-256 no cambian).
- Los .json (manifiestos, resúmenes) se copian con cualquier ruta local (unidad de disco, carpeta de usuario) reducida al nombre
  del archivo, y con una clave `redaction_note`. Por eso su SHA-256 difiere del original, que se conserva en el equipo.
- No sobrescribe: si el destino existe, se detiene.

Uso (desde la raíz del repo):  python tools/publish_results.py
"""
import json
import pathlib
import re
import shutil
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCES = {  # carpeta publicada -> (carpeta local de origen excluida de git, patrón de archivos)
    'format_tuning_r1': ('runner/runs_dev', '*'),
    'format_tuning_r2': ('runner/runs_dev_r2', '*'),
    'pilot_qwen3_0.6b': ('runner/runs_pilot', '*'),
    'scorer_validation_dev': ('runner/runs', '*a7370f*'),  # primera corrida exploratoria sobre dev que validó el corrector
}
LOCAL = re.compile(r'^[A-Za-z]:[\\/]|[\\/]Users[\\/]|OneDrive')
NOTE = ('Rutas locales redactadas antes de publicar. El resto del contenido es el original; el SHA-256 de este archivo '
        'difiere del original, que se conserva en el equipo del investigador.')


def clean(v):
    """Devuelve (valor limpio, ¿hubo cambios?)."""
    if isinstance(v, str):
        if LOCAL.search(v):
            return v.replace('\\', '/').rstrip('/').rsplit('/', 1)[-1], True
        return v, False
    if isinstance(v, list):
        pairs = [clean(x) for x in v]
        return [p[0] for p in pairs], any(p[1] for p in pairs)
    if isinstance(v, dict):
        pairs = {k: clean(x) for k, x in v.items()}
        return {k: p[0] for k, p in pairs.items()}, any(p[1] for p in pairs.values())
    return v, False


def main():
    n_copied = n_redacted = 0
    for dest_name, (src_rel, pattern) in SOURCES.items():
        src, dest = ROOT / src_rel, ROOT / 'results' / dest_name
        if not src.exists():
            raise SystemExit(f'No existe el origen {src}')
        if dest.exists():
            print(f'{dest_name}: ya existe, no se sobrescribe (se omite)')
            continue
        dest.mkdir(parents=True)
        for f in sorted(src.glob(pattern)):
            if not f.is_file():
                continue
            if f.suffix == '.json':
                data = json.loads(f.read_text(encoding='utf-8-sig'))
                cleaned, changed = clean(data)
                if changed and isinstance(cleaned, dict):
                    cleaned['redaction_note'] = NOTE
                    n_redacted += 1
                with (dest / f.name).open('x', encoding='utf-8', newline='\n') as out:
                    json.dump(cleaned, out, ensure_ascii=False, indent=2)
                    out.write('\n')
            else:
                shutil.copyfile(f, dest / f.name)
            n_copied += 1
    print(f'{n_copied} archivos copiados a results/ ({n_redacted} con rutas redactadas)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
