# Informe de cobertura del benchmark v1

Generado a partir de `coverage_report_v1.csv` y `validation_v1.json`. Total: **180 ítems**, 73 familias.

| Competencia | Fila | Págs. | Estado | Ítems | % | A | B | C | Básica | Interm. | Avanz. | Familias | Controles B | Con cero |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| NAT-READ-WRITE | AR-01 | 188-190 | habilitada | 6 | 3.3 | 2 | 2 | 2 | 0 | 3 | 3 | 2 | 0 | 6 |
| NAT-SKIP-COUNT | AR-01 | 190 | habilitada | 6 | 3.3 | 2 | 2 | 2 | 3 | 3 | 0 | 2 | 0 | 6 |
| NAT-ORDER-COMPARE | AR-02 | 191 | habilitada | 9 | 5.0 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 0 | 9 |
| NAT-PLACE-VALUE | AR-03 | 192-193 | habilitada | 12 | 6.7 | 4 | 4 | 4 | 3 | 6 | 3 | 4 | 0 | 12 |
| ADD-4DIG | AR-04 | 193-194 | habilitada | 16 | 8.9 | 5 | 6 | 5 | 7 | 5 | 4 | 7 | 2 | 7 |
| ADD-PROPERTIES | AR-04 | 194 | habilitada | 6 | 3.3 | 2 | 2 | 2 | 3 | 3 | 0 | 2 | 0 | 6 |
| SUB-10K | AR-05 | 194-195 | habilitada | 16 | 8.9 | 5 | 6 | 5 | 7 | 5 | 4 | 7 | 2 | 7 |
| SUB-CHECK-REINTEGRATIVE | AR-05 | 194-195 | habilitada | 2 | 1.1 | 2 | 0 | 0 | 0 | 1 | 1 | 2 | 0 | 0 |
| MUL-TABLES-1-12 | AR-06 | 195-196 | habilitada | 16 | 8.9 | 5 | 5 | 6 | 7 | 5 | 4 | 7 | 1 | 0 |
| MUL-POW10 | AR-06 | 196 | habilitada | 9 | 5.0 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 0 | 9 |
| MUL-TENS | AR-06 | 196 | pendiente de interpretación | 0 | 0.0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| DIV-EXACT | AR-07 | 197 | habilitada | 9 | 5.0 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 0 | 9 |
| DIV-INEXACT | AR-07 | 197 | habilitada | 14 | 7.8 | 4 | 5 | 5 | 6 | 4 | 4 | 6 | 1 | 6 |
| DIV-POW10 | AR-07 | 197 | habilitada | 10 | 5.6 | 4 | 3 | 3 | 4 | 3 | 3 | 4 | 0 | 10 |
| DIV-CHECK-REINTEGRATIVE | AR-07 | 197 | habilitada | 1 | 0.6 | 1 | 0 | 0 | 0 | 0 | 1 | 1 | 0 | 0 |
| COMBINED-OPS | AR-04; AR-05; AR-06; AR-07 | 197 | habilitada | 12 | 6.7 | 4 | 4 | 4 | 0 | 7 | 5 | 5 | 1 | 7 |
| ORD-1-50 | AR-08 | 198-199 | habilitada | 8 | 4.4 | 3 | 2 | 3 | 3 | 3 | 2 | 3 | 0 | 0 |
| FRAC-REPR-CLASSIFY | AR-09 | 199 | habilitada | 8 | 4.4 | 2 | 3 | 3 | 5 | 3 | 0 | 3 | 0 | 0 |
| FRAC-COMPARE-HOMOG | AR-10 | 200 | habilitada | 9 | 5.0 | 3 | 3 | 3 | 3 | 4 | 2 | 4 | 1 | 0 |
| FRAC-ADDSUB-HOMOG | AR-11 | 201 | habilitada | 11 | 6.1 | 3 | 4 | 4 | 4 | 4 | 3 | 5 | 1 | 0 |
| FRAC-EQUIV | AR-12 | 201-202 | solo piloto | 0 | 0.0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

## Totales

- Por tarea: {'problem_solving': 60, 'error_diagnosis': 60, 'hint_generation': 60}
- Por dificultad propuesta: {'intermediate': 68, 'advanced_in_grade': 48, 'basic': 64}
- Casos de control en diagnóstico (trabajo correcto): 9
- Ítems que involucran el cero (en cifras, operandos o respuesta): 94
- Mayor participación de una sola competencia: 8.9 %

## Desequilibrios y ausencias

- Con pocos ítems (menos de 6): SUB-CHECK-REINTEGRATIVE, DIV-CHECK-REINTEGRATIVE. Solo admiten la tarea A (no tienen un error estudiantil natural que simular).
- Competencias sin ítems: MUL-TENS, FRAC-EQUIV (por diseño: `FRAC-EQUIV` solo en piloto y `MUL-TENS` pendiente de interpretación).
- Las competencias con operaciones (adición, sustracción, multiplicación, división) pesan más porque el programa las desarrolla con más contenido.
- Las etiquetas de dificultad son de diseño, no empíricas.
