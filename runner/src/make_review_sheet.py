"""Genera un CSV de anotacion para revisión humana de resultados."""
import argparse
import csv
import json
import pathlib

fields = ['id','task','topic','model','response','gold_answer','gold_error',
          'correctitud_matematica_0_a_2','diagnostico_0_a_2',
          'utilidad_pista_0_a_2','adecuacion_edad_0_a_2',
          'revela_respuesta_si_no','observaciones','evaluador']

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--input',required=True)
    p.add_argument('--output',default=None)
    a = p.parse_args()
    src=pathlib.Path(a.input)
    dest=pathlib.Path(a.output) if a.output else src.with_suffix('.review.csv')
    with src.open(encoding='utf-8') as f, dest.open('w',encoding='utf-8',newline='') as out:
        w=csv.DictWriter(out,fieldnames=fields)
        w.writeheader()
        for line in f:
            if line.strip():
                x=json.loads(line)
                w.writerow({k:x.get(k,'') for k in fields})
    print(dest)

if __name__=='__main__': main()
