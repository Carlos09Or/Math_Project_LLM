"""Sondas de FORMATO: 12 problemas ADICIONALES, fuera del dataset de evaluación (items.jsonl).

Sirven solo para ajustar el formato de salida de los prompts (que el corrector pueda leer la respuesta)
sin sobreajustar a la partición `dev` ni tocar `pilot`. NO son datos de evaluación y no se reportan como resultados.
Sus operandos no coinciden con los de ningún problema de problem_bases.py (lo comprueba una prueba).

Uso:  python src/format_probes.py        (escribe data/format_probes.jsonl; falla si existe)
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import build_dataset as bd  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1]
SUB, MUL, DIV = 'A3-SUB-24', 'A3-MUL-24', 'A3-DIV-24'

PROBE_BASES = [
    ('PRB-SUB-01', SUB, 'sub', 834, 267, 'Una tienda tenía 834 lápices y vendió 267 lápices. ¿Cuántos lápices le quedan?', 'error:sub_col_min_from_max', 'dev'),
    ('PRB-SUB-02', SUB, 'sub', 1520, 693, 'Un bus recorrió 1520 kilómetros en el mes y 693 fueron por carretera. ¿Cuántos kilómetros recorrió fuera de la carretera?', 'error:sub_borrow_no_decrement', 'dev'),
    ('PRB-SUB-03', SUB, 'sub', 6005, 2378, 'Una granja tenía 6005 huevos y vendió 2378 huevos. ¿Cuántos huevos le quedan?', 'error:sub_col_min_from_max', 'dev'),
    ('PRB-SUB-04', SUB, 'sub', 3150, 1428, 'En un mercado había 3150 mangos y se vendieron 1428 mangos. ¿Cuántos mangos quedan?', 'error:sub_add_instead', 'dev'),
    ('PRB-MUL-01', MUL, 'mul', 17, 5, 'Cada bolsa tiene 17 caramelos. ¿Cuántos caramelos hay en 5 bolsas?', 'error:mul_omit_carry', 'dev'),
    ('PRB-MUL-02', MUL, 'mul', 32, 18, 'En un salón hay 18 mesas con 32 hojas en cada una. ¿Cuántas hojas hay en total?', 'error:mul_forget_shift', 'dev'),
    ('PRB-MUL-03', MUL, 'mul', 214, 7, 'Una librería recibe 214 cuadernos cada día. ¿Cuántos cuadernos recibe en 7 días?', 'error:mul_add_instead', 'dev'),
    ('PRB-MUL-04', MUL, 'mul', 1050, 6, 'Una fábrica produce 1050 botellas cada hora. ¿Cuántas botellas produce en 6 horas?', 'error:mul_omit_carry', 'dev'),
    ('PRB-DIV-01', DIV, 'div', 96, 5, 'Se reparten 96 galletas por igual entre 5 niños. ¿Cuántas galletas recibe cada niño y cuántas sobran?', 'error:div_stop_early', 'dev'),
    ('PRB-DIV-02', DIV, 'div', 250, 7, 'Un panadero acomoda 250 panes por igual en 7 bandejas. ¿Cuántos panes lleva cada bandeja y cuántos sobran?', 'error:div_ignore_remainder', 'dev'),
    ('PRB-DIV-03', DIV, 'div', 384, 16, 'Una escuela organiza 384 estudiantes por igual en 16 grupos. ¿Cuántos estudiantes hay en cada grupo y cuántos sobran?', 'error:div_subtract_instead', 'dev'),
    ('PRB-DIV-04', DIV, 'div', 703, 9, 'Una finca empaca 703 naranjas por igual en 9 cajas. ¿Cuántas naranjas lleva cada caja y cuántas sobran?', 'error:div_stop_early', 'dev'),
]


# Ronda 2: 12 problemas NUEVOS (la ronda 1 ya se vio, reutilizarla sobreajustaría). Operandos distintos de los del
# dataset y de las sondas de la ronda 1 (lo comprueba una prueba).
PROBE_BASES_R2 = [
    ('PRC-SUB-01', SUB, 'sub', 913, 478, 'Un taller tenía 913 tornillos y usó 478 tornillos. ¿Cuántos tornillos le quedan?', 'error:sub_col_min_from_max', 'dev'),
    ('PRC-SUB-02', SUB, 'sub', 2040, 1365, 'Una escuela tenía 2040 sillas y prestó 1365 sillas a otra escuela. ¿Cuántas sillas le quedan?', 'error:sub_borrow_no_decrement', 'dev'),
    ('PRC-SUB-03', SUB, 'sub', 5230, 2987, 'Un camión llevaba 5230 kilos de arroz y entregó 2987 kilos. ¿Cuántos kilos de arroz le quedan?', 'error:sub_col_min_from_max', 'dev'),
    ('PRC-SUB-04', SUB, 'sub', 8002, 3419, 'Una cooperativa tenía B/.8002 y gastó B/.3419. ¿Cuántos balboas le quedan?', 'error:sub_borrow_no_decrement', 'dev'),
    ('PRC-MUL-01', MUL, 'mul', 26, 4, 'Cada fila tiene 26 sillas. ¿Cuántas sillas hay en 4 filas?', 'error:mul_omit_carry', 'dev'),
    ('PRC-MUL-02', MUL, 'mul', 45, 12, 'Un huerto tiene 12 surcos con 45 plantas en cada surco. ¿Cuántas plantas hay en total?', 'error:mul_forget_shift', 'dev'),
    ('PRC-MUL-03', MUL, 'mul', 308, 9, 'Un ciclista recorre 308 metros por minuto. ¿Cuántos metros recorre en 9 minutos?', 'error:mul_add_instead', 'dev'),
    ('PRC-MUL-04', MUL, 'mul', 1260, 5, 'Una panadería usa 1260 gramos de harina por día. ¿Cuántos gramos usa en 5 días?', 'error:mul_omit_carry', 'dev'),
    ('PRC-DIV-01', DIV, 'div', 83, 6, 'Se reparten 83 fichas por igual entre 6 jugadores. ¿Cuántas fichas recibe cada jugador y cuántas sobran?', 'error:div_stop_early', 'dev'),
    ('PRC-DIV-02', DIV, 'div', 305, 8, 'Una maestra reparte 305 hojas por igual en 8 carpetas. ¿Cuántas hojas lleva cada carpeta y cuántas sobran?', 'error:div_ignore_remainder', 'dev'),
    ('PRC-DIV-03', DIV, 'div', 432, 18, 'Un club ordena 432 libros por igual en 18 estantes. ¿Cuántos libros lleva cada estante y cuántos sobran?', 'error:div_subtract_instead', 'dev'),
    ('PRC-DIV-04', DIV, 'div', 968, 21, 'Una finca empaca 968 limones por igual en 21 cajas. ¿Cuántos limones lleva cada caja y cuántos sobran?', 'error:div_stop_early', 'dev'),
]


def main(argv=None):
    import argparse
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument('--round', type=int, choices=(1, 2), default=1)
    a = p.parse_args(argv)
    bases, name = (PROBE_BASES, 'format_probes.jsonl') if a.round == 1 else (PROBE_BASES_R2, 'format_probes_r2.jsonl')
    out = ROOT / 'data' / name
    if out.exists():
        raise SystemExit(f'Ya existe {out}; no se sobrescribe.')
    items = bd.build_items(bases)
    with out.open('x', encoding='utf-8', newline='\n') as f:
        for it in items:
            f.write(json.dumps({k: it[k] for k in bd.FIELDS}, ensure_ascii=False, separators=(',', ':')) + '\n')
    print(f'{len(items)} ítems de {len(bases)} problemas -> {out}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
